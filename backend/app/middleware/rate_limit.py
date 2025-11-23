"""
Rate limiting middleware using Redis
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import logging
from typing import Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established for rate limiting")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Rate limiting disabled.")
            self.redis_client = None
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        if self.redis_client is None:
            # Rate limiting disabled if Redis unavailable
            return await call_next(request)
        
        # Get client identifier (IP or user ID)
        client_id = self._get_client_id(request)
        
        # Check rate limit
        endpoint = request.url.path
        rate_limit_key = self._get_rate_limit_config(endpoint)
        
        if rate_limit_key:
            is_allowed, remaining = self._check_rate_limit(client_id, rate_limit_key)
            
            if not is_allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
        
        response = await call_next(request)
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get user ID from token if authenticated
        # For now, use IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"client:{client_ip}"
    
    def _get_rate_limit_config(self, endpoint: str) -> Tuple[int, int]:
        """
        Get rate limit configuration for endpoint
        
        Returns:
            Tuple of (limit, window_seconds)
        """
        # Map endpoints to rate limit configs
        if "/posts" in endpoint and endpoint.endswith("/posts/"):
            limit, window = settings.RATE_LIMIT_NEW_POST.split(":")
            return (int(limit), int(window))
        
        elif "/responses" in endpoint:
            limit, window = settings.RATE_LIMIT_FEEDBACK.split(":")
            return (int(limit), int(window))
        
        # Default API rate limit
        limit, window = settings.RATE_LIMIT_API_CALL.split(":")
        return (int(limit), int(window))
    
    def _check_rate_limit(self, client_id: str, config: Tuple[int, int]) -> Tuple[bool, int]:
        """
        Check if request is within rate limit
        
        Args:
            client_id: Client identifier
            config: (limit, window_seconds) tuple
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        limit, window = config
        key = f"rate_limit:{client_id}"
        
        try:
            current = self.redis_client.get(key)
            
            if current is None:
                # First request in window
                self.redis_client.setex(key, window, 1)
                return (True, limit - 1)
            
            current_count = int(current)
            
            if current_count >= limit:
                return (False, 0)
            
            # Increment counter
            self.redis_client.incr(key)
            return (True, limit - current_count - 1)
        
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # Allow request if rate limit check fails
            return (True, limit)
