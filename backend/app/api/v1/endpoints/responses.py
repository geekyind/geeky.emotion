"""
Response/feedback endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
import uuid
import logging

from app.services.moderation_service import moderation_service
from app.api.v1.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateResponseRequest(BaseModel):
    post_id: str
    content: str
    response_type: Optional[str] = "peer"  # peer or professional


class ResponseModel(BaseModel):
    id: str
    post_id: str
    anonymous_id: str
    content: str
    response_type: str
    created_at: str
    helpful_count: int = 0


@router.post("/", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def create_response(
    request: CreateResponseRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a response/feedback to a post
    """
    try:
        # Moderate response content
        moderation_result = await moderation_service.moderate_content(
            content=request.content,
            anonymous_id=current_user['anonymous_id']
        )
        
        if not moderation_result['approved']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Response content does not meet community guidelines"
            )
        
        response_id = str(uuid.uuid4())
        
        # In production, save to database
        
        logger.info(f"Response created: {response_id} for post {request.post_id}")
        
        return ResponseModel(
            id=response_id,
            post_id=request.post_id,
            anonymous_id=current_user['anonymous_id'],
            content=request.content,
            response_type=request.response_type,
            created_at="2025-11-23T00:00:00Z",
            helpful_count=0
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create response"
        )


@router.get("/{post_id}")
async def get_responses(
    post_id: str,
    skip: int = 0,
    limit: int = 20
):
    """
    Get all responses for a post
    """
    # In production, fetch from database
    return {
        "post_id": post_id,
        "responses": [],
        "total": 0
    }


@router.post("/{response_id}/helpful")
async def mark_helpful(
    response_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a response as helpful
    """
    # In production, update database
    return {
        "response_id": response_id,
        "marked_helpful": True
    }
