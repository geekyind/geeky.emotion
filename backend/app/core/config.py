"""
Application configuration using Pydantic settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database URLs
    DATABASE_URL: str
    DATABASE_IDENTITY_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    
    # AWS Cognito
    COGNITO_USER_POOL_ID: str
    COGNITO_CLIENT_ID: str
    COGNITO_REGION: str = "us-east-1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str
    SALT_SECRET: str
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate Limiting (format: limit:window_seconds)
    RATE_LIMIT_NEW_POST: str = "10:3600"
    RATE_LIMIT_FEEDBACK: str = "50:3600"
    RATE_LIMIT_REPORT: str = "20:86400"
    RATE_LIMIT_API_CALL: str = "1000:60"
    
    # ML Models
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    TOXICITY_MODEL: str = "unitary/toxic-bert"
    
    # Monitoring
    SENTRY_DSN: str = ""
    PROMETHEUS_PORT: int = 9090
    
    # Crisis Resources
    CRISIS_HOTLINE_US: str = "988"
    CRISIS_HOTLINE_UK: str = "116123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
