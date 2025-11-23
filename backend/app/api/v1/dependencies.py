"""
API dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Validate JWT token and return current user information
    
    Args:
        credentials: Bearer token from Authorization header
    
    Returns:
        Dictionary with user information (user_sub, anonymous_id, email)
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        token = credentials.credentials
        
        # Verify token with Cognito
        user_info = await auth_service.verify_token(token)
        
        return user_info
    
    except ValueError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def require_moderator(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Require user to have moderator role
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User information if authorized
    
    Raises:
        HTTPException: If user doesn't have moderator role
    """
    # In production, check user roles from Cognito groups or database
    # For now, this is a placeholder
    
    # Example: Check if user is in moderator group
    # if 'moderator' not in current_user.get('groups', []):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Moderator access required"
    #     )
    
    return current_user


async def require_professional(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Require user to have professional (therapist/counselor) role
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User information if authorized
    
    Raises:
        HTTPException: If user doesn't have professional role
    """
    # In production, check professional verification status
    # For now, this is a placeholder
    
    return current_user
