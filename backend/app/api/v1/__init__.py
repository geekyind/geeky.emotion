"""
API routes configuration
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, posts, responses, moderation, user

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(responses.router, prefix="/responses", tags=["responses"])
api_router.include_router(moderation.router, prefix="/moderation", tags=["moderation"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
