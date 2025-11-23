"""
Security utilities for encryption, hashing, and token management
"""
import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption cipher
cipher = Fernet(settings.ENCRYPTION_KEY.encode() if len(settings.ENCRYPTION_KEY) == 44 
                else Fernet.generate_key())


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_anonymous_id(user_id: str, email: str) -> str:
    """
    Generate cryptographic anonymous ID using HMAC-SHA256
    
    Args:
        user_id: User's unique identifier (Cognito sub)
        email: User's email address
    
    Returns:
        Anonymous ID in format: anon_[16-char-hex]
    """
    salt = secrets.token_bytes(32)
    hash_input = f"{user_id}{email}{settings.SALT_SECRET}{salt.hex()}".encode()
    anonymous_id = hashlib.sha256(hash_input).hexdigest()[:16]
    
    return f"anon_{anonymous_id}"


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    return cipher.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return cipher.decrypt(encrypted_data.encode()).decode()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data to encode in token
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)


def scrub_pii(text: str) -> str:
    """
    Remove personally identifiable information from text
    
    This is a basic implementation. In production, use more sophisticated
    NLP models for PII detection.
    
    Args:
        text: Input text to scrub
    
    Returns:
        Text with PII removed/redacted
    """
    import re
    
    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Phone numbers (US format)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Social Security Numbers
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Credit card numbers
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
    
    # Zip codes
    text = re.sub(r'\b\d{5}(?:-\d{4})?\b', '[ZIP]', text)
    
    # IP addresses
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', text)
    
    return text
