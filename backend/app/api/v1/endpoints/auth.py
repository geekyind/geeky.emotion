"""
Authentication endpoints
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import logging

from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)

router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpResponse(BaseModel):
    user_sub: str
    anonymous_id: str
    status: str
    message: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    anonymous_id: str
    expires_in: int


class ConfirmSignUpRequest(BaseModel):
    email: EmailStr
    confirmation_code: str


@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(request: SignUpRequest):
    """
    Register a new user with email and password
    """
    try:
        result = await auth_service.sign_up(request.email, request.password)
        
        return SignUpResponse(
            user_sub=result['user_sub'],
            anonymous_id=result['anonymous_id'],
            status=result['status'],
            message="Registration successful. Please check your email to verify your account."
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Sign up error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/confirm", status_code=status.HTTP_200_OK)
async def confirm_sign_up(request: ConfirmSignUpRequest):
    """
    Confirm user registration with verification code
    """
    try:
        await auth_service.confirm_sign_up(request.email, request.confirmation_code)
        
        return {
            "message": "Email verified successfully. You can now sign in.",
            "verified": True
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/signin", response_model=SignInResponse)
async def sign_in(request: SignInRequest):
    """
    Authenticate user and return access tokens
    """
    try:
        result = await auth_service.authenticate(request.email, request.password)
        
        return SignInResponse(
            access_token=result['access_token'],
            refresh_token=result['refresh_token'],
            anonymous_id=result['anonymous_id'],
            expires_in=result['expires_in']
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    try:
        result = await auth_service.refresh_token(refresh_token)
        
        return {
            "access_token": result['access_token'],
            "token_type": "bearer",
            "expires_in": result['expires_in']
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/forgot-password")
async def forgot_password(email: EmailStr):
    """
    Initiate password reset flow
    """
    try:
        await auth_service.forgot_password(email)
        
        return {
            "message": "Password reset code sent to your email.",
            "success": True
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    confirmation_code: str
    new_password: str


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Complete password reset with confirmation code
    """
    try:
        await auth_service.confirm_forgot_password(
            request.email,
            request.confirmation_code,
            request.new_password
        )
        
        return {
            "message": "Password reset successful. You can now sign in with your new password.",
            "success": True
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
