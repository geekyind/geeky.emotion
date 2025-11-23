"""
Database models for user identity (separate database)
"""
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text
from sqlalchemy.sql import func

from app.core.database import IdentityBase


class UserIdentity(IdentityBase):
    """User identity information (stored separately from content)"""
    __tablename__ = "user_identities"
    
    # Cognito User Sub (primary key)
    user_sub = Column(String(128), primary_key=True, index=True)
    
    # Anonymous ID mapping (encrypted)
    anonymous_id = Column(String(64), unique=True, index=True, nullable=False)
    
    # Basic info (from Cognito)
    email = Column(String(255), unique=True, index=True, nullable=False)
    email_verified = Column(Boolean, default=False)
    
    # Account status
    account_status = Column(String(20), default="active")  # active, suspended, deleted
    suspension_reason = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Privacy settings
    privacy_settings = Column(JSON, default=dict)
    
    # Trust level
    trust_level = Column(String(20), default="new")  # new, established, trusted
    trust_score = Column(Integer, default=0)


class AuditLog(IdentityBase):
    """Audit log for sensitive operations"""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, index=True)
    user_sub = Column(String(128), index=True, nullable=True)
    anonymous_id = Column(String(64), index=True, nullable=True)
    
    # Action details
    action_type = Column(String(50), index=True, nullable=False)
    action_description = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(128), nullable=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Result
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Additional metadata
    metadata = Column(JSON, default=dict)
