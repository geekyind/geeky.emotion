"""
Authentication service with AWS Cognito integration
"""
import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional, Dict
import jwt
from jwt import PyJWKClient

from app.core.config import settings
from app.core.security import generate_anonymous_id

logger = logging.getLogger(__name__)


class AuthService:
    """AWS Cognito authentication service"""
    
    def __init__(self):
        self.cognito = boto3.client(
            'cognito-idp',
            region_name=settings.COGNITO_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID
        
        # JWKS client for token verification
        jwks_url = (
            f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/"
            f"{self.user_pool_id}/.well-known/jwks.json"
        )
        self.jwks_client = PyJWKClient(jwks_url)
    
    async def sign_up(self, email: str, password: str) -> Dict:
        """
        Register new user with automatic anonymous ID generation
        
        Args:
            email: User's email address
            password: User's password
        
        Returns:
            Dictionary with user_sub and anonymous_id
        
        Raises:
            ValueError: If email already exists or registration fails
        """
        try:
            # Generate anonymous ID before Cognito registration
            temp_user_id = email  # Temporary ID until we get Cognito sub
            anonymous_id = generate_anonymous_id(temp_user_id, email)
            
            response = self.cognito.sign_up(
                ClientId=self.client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'custom:anonymous_id', 'Value': anonymous_id}
                ]
            )
            
            logger.info(f"User registered successfully: {anonymous_id}")
            
            return {
                'user_sub': response['UserSub'],
                'anonymous_id': anonymous_id,
                'status': 'pending_verification',
                'email': email
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'UsernameExistsException':
                raise ValueError("Email already registered")
            elif error_code == 'InvalidPasswordException':
                raise ValueError("Password does not meet requirements")
            elif error_code == 'InvalidParameterException':
                raise ValueError("Invalid email or password format")
            else:
                logger.error(f"Cognito sign up error: {e}")
                raise ValueError(f"Registration failed: {error_code}")
    
    async def confirm_sign_up(self, email: str, confirmation_code: str) -> bool:
        """
        Confirm user registration with verification code
        
        Args:
            email: User's email address
            confirmation_code: Verification code sent to email
        
        Returns:
            True if confirmation successful
        """
        try:
            self.cognito.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code
            )
            
            logger.info(f"User confirmed: {email}")
            return True
            
        except ClientError as e:
            logger.error(f"Confirmation error: {e}")
            raise ValueError(f"Confirmation failed: {e.response['Error']['Code']}")
    
    async def authenticate(self, email: str, password: str) -> Dict:
        """
        Authenticate user and return tokens
        
        Args:
            email: User's email
            password: User's password
        
        Returns:
            Dictionary with access_token, refresh_token, id_token, anonymous_id
        """
        try:
            response = self.cognito.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            # Extract tokens
            auth_result = response['AuthenticationResult']
            access_token = auth_result['AccessToken']
            
            # Get user attributes to retrieve anonymous_id
            user_info = await self.get_user_info(access_token)
            
            return {
                'access_token': access_token,
                'refresh_token': auth_result.get('RefreshToken'),
                'id_token': auth_result['IdToken'],
                'anonymous_id': user_info.get('custom:anonymous_id'),
                'expires_in': auth_result['ExpiresIn'],
                'email': user_info.get('email')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'NotAuthorizedException':
                raise ValueError("Invalid credentials")
            elif error_code == 'UserNotConfirmedException':
                raise ValueError("Email not verified")
            elif error_code == 'PasswordResetRequiredException':
                raise ValueError("Password reset required")
            else:
                logger.error(f"Authentication error: {e}")
                raise ValueError(f"Authentication failed: {error_code}")
    
    async def get_user_info(self, access_token: str) -> Dict:
        """
        Get user attributes from Cognito
        
        Args:
            access_token: Valid Cognito access token
        
        Returns:
            Dictionary of user attributes
        """
        try:
            response = self.cognito.get_user(AccessToken=access_token)
            
            user_attributes = {}
            for attr in response['UserAttributes']:
                user_attributes[attr['Name']] = attr['Value']
            
            return user_attributes
            
        except ClientError as e:
            logger.error(f"Get user info error: {e}")
            raise ValueError("Failed to retrieve user information")
    
    async def verify_token(self, token: str) -> Dict:
        """
        Verify Cognito JWT token
        
        Args:
            token: JWT token to verify
        
        Returns:
            Decoded token payload with user information
        """
        try:
            # Get signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id,
                options={"verify_exp": True}
            )
            
            return {
                'user_sub': payload['sub'],
                'anonymous_id': payload.get('custom:anonymous_id'),
                'email': payload.get('email'),
                'token_use': payload.get('token_use'),
                'exp': payload.get('exp')
            }
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Token verification error: {e}")
            raise ValueError("Invalid token")
    
    async def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid Cognito refresh token
        
        Returns:
            New access and id tokens
        """
        try:
            response = self.cognito.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            auth_result = response['AuthenticationResult']
            
            return {
                'access_token': auth_result['AccessToken'],
                'id_token': auth_result['IdToken'],
                'expires_in': auth_result['ExpiresIn']
            }
            
        except ClientError as e:
            logger.error(f"Token refresh error: {e}")
            raise ValueError("Failed to refresh token")
    
    async def forgot_password(self, email: str) -> bool:
        """
        Initiate password reset flow
        
        Args:
            email: User's email address
        
        Returns:
            True if reset email sent
        """
        try:
            self.cognito.forgot_password(
                ClientId=self.client_id,
                Username=email
            )
            
            logger.info(f"Password reset initiated for: {email}")
            return True
            
        except ClientError as e:
            logger.error(f"Forgot password error: {e}")
            raise ValueError("Failed to initiate password reset")
    
    async def confirm_forgot_password(
        self,
        email: str,
        confirmation_code: str,
        new_password: str
    ) -> bool:
        """
        Complete password reset with confirmation code
        
        Args:
            email: User's email address
            confirmation_code: Reset confirmation code
            new_password: New password
        
        Returns:
            True if password reset successful
        """
        try:
            self.cognito.confirm_forgot_password(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=new_password
            )
            
            logger.info(f"Password reset completed for: {email}")
            return True
            
        except ClientError as e:
            logger.error(f"Confirm forgot password error: {e}")
            raise ValueError("Failed to reset password")


# Singleton instance
auth_service = AuthService()
