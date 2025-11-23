"""
Post endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
import hashlib
import logging

from app.services.anonymization_service import anonymization_service
from app.services.moderation_service import moderation_service
from app.services.similar_post_service import similar_post_service
from app.api.v1.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class CreatePostRequest(BaseModel):
    content: str
    topics: Optional[List[str]] = []
    emotional_intensity: Optional[int] = 5


class PostResponse(BaseModel):
    id: str
    anonymous_id: str
    content: str
    topics: List[str]
    emotional_intensity: int
    created_at: str
    moderation_status: str
    response_count: int = 0


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: CreatePostRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new anonymous post
    """
    try:
        # Anonymize post content
        anonymized = anonymization_service.anonymize_post(
            user_id=current_user['user_sub'],
            email=current_user['email'],
            content=request.content,
            metadata={
                'topics': request.topics,
                'emotional_intensity': request.emotional_intensity
            }
        )
        
        # Moderate content
        moderation_result = await moderation_service.moderate_content(
            content=anonymized['content'],
            anonymous_id=anonymized['anonymous_id'],
            context=anonymized['context']
        )
        
        # Handle crisis detection
        if moderation_result['crisis_detected']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "crisis_detected",
                    "message": "We're concerned about your safety. Please consider reaching out to a crisis counselor.",
                    "resources": {
                        "us_hotline": "988",
                        "crisis_text": "Text HOME to 741741"
                    }
                }
            )
        
        # Generate post ID
        post_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(anonymized['content'].encode()).hexdigest()
        
        # Store post (in production, save to database)
        # For now, return response
        
        # Index post for similarity search
        await similar_post_service.index_post(
            post_id=post_id,
            content=anonymized['content'],
            metadata={
                'topics': request.topics,
                'emotional_intensity': request.emotional_intensity,
                'has_positive_resolution': False,
                'response_count': 0
            }
        )
        
        logger.info(f"Post created: {post_id} by {anonymized['anonymous_id']}")
        
        return PostResponse(
            id=post_id,
            anonymous_id=anonymized['anonymous_id'],
            content=anonymized['content'],
            topics=request.topics,
            emotional_intensity=request.emotional_intensity,
            created_at=anonymized['timestamp'].isoformat(),
            moderation_status=moderation_result['severity'],
            response_count=0
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post"
        )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    """
    Get a post by ID
    """
    # In production, fetch from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )


@router.get("/similar/{post_id}")
async def get_similar_posts(
    post_id: str,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Find posts similar to the given post
    """
    try:
        # In production, fetch post content from database
        # For now, return mock data
        post_content = "I'm feeling anxious about my future"
        
        similar_posts = await similar_post_service.find_similar_posts(
            query_content=post_content,
            top_k=limit,
            similarity_threshold=0.7,
            filters={
                'has_positive_resolution': True,
                'moderation_approved': True
            }
        )
        
        return {
            "post_id": post_id,
            "similar_posts": similar_posts,
            "count": len(similar_posts)
        }
    
    except Exception as e:
        logger.error(f"Error finding similar posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar posts"
        )


@router.get("/")
async def list_posts(
    skip: int = 0,
    limit: int = 20,
    topic: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List posts with pagination and filtering
    """
    # In production, fetch from database with filters
    return {
        "posts": [],
        "total": 0,
        "skip": skip,
        "limit": limit
    }
