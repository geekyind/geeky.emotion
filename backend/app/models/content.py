"""
Database models for content (anonymous posts)
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import ContentBase


class Post(ContentBase):
    """Anonymous user post model"""
    __tablename__ = "posts"
    
    id = Column(String(36), primary_key=True, index=True)
    anonymous_id = Column(String(64), index=True, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), unique=True, nullable=False)
    
    # Metadata
    topics = Column(JSON, default=list)
    emotional_intensity = Column(Integer, default=5)
    word_count = Column(Integer)
    
    # Timestamps (fuzzed)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Moderation
    moderation_status = Column(String(20), default="pending", index=True)
    severity_level = Column(String(20), default="safe")
    moderation_flags = Column(JSON, default=list)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Engagement
    response_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    has_positive_resolution = Column(Boolean, default=False)
    
    # ML embeddings (stored as JSON for simplicity)
    embedding = Column(JSON, nullable=True)


class Response(ContentBase):
    """Response/feedback to posts"""
    __tablename__ = "responses"
    
    id = Column(String(36), primary_key=True, index=True)
    post_id = Column(String(36), index=True, nullable=False)
    anonymous_id = Column(String(64), index=True, nullable=False)
    
    content = Column(Text, nullable=False)
    response_type = Column(String(20), default="peer")  # peer, professional
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Engagement
    helpful_count = Column(Integer, default=0)
    is_verified_professional = Column(Boolean, default=False)
    
    # Moderation
    moderation_status = Column(String(20), default="approved")


class ModerationQueue(ContentBase):
    """Queue for content requiring moderation"""
    __tablename__ = "moderation_queue"
    
    id = Column(String(36), primary_key=True, index=True)
    content_id = Column(String(36), index=True, nullable=False)
    content_type = Column(String(20), nullable=False)  # post, response
    
    severity = Column(String(20), index=True, nullable=False)
    flags = Column(JSON, default=list)
    
    # Queue management
    assigned_to = Column(String(64), nullable=True)
    sla_hours = Column(Integer, nullable=False)
    queued_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Decision
    decision = Column(String(20), nullable=True)  # approved, rejected, escalated
    decision_notes = Column(Text, nullable=True)


class CrisisIntervention(ContentBase):
    """Track crisis interventions"""
    __tablename__ = "crisis_interventions"
    
    id = Column(String(36), primary_key=True, index=True)
    anonymous_id = Column(String(64), index=True, nullable=False)
    post_id = Column(String(36), nullable=True)
    
    crisis_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    
    # Intervention
    resources_shown = Column(JSON, default=list)
    user_action = Column(String(50), nullable=True)  # contacted_hotline, continued, etc.
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Follow-up
    follow_up_required = Column(Boolean, default=True)
    follow_up_completed = Column(Boolean, default=False)
