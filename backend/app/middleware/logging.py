"""
Logging middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import json

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        """Log requests and responses"""
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} ({duration:.3f}s)",
                extra={
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                    "path": request.url.path
                }
            )
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"Request failed: {str(e)} ({duration:.3f}s)",
                extra={
                    "error": str(e),
                    "duration_seconds": duration,
                    "path": request.url.path
                },
                exc_info=True
            )
            
            raise
