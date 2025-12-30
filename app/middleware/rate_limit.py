"""
Rate Limiting Middleware
Implements rate limiting for API endpoints to prevent abuse and brute force attacks
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
import os

logger = logging.getLogger(__name__)

# Determine storage type (memory or redis)
# Use Redis if available, otherwise use memory
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Try to use Redis if available, fallback to memory
try:
    import redis
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
    redis_client.ping()
    storage_uri = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    logger.info(f"Using Redis for rate limiting: {storage_uri}")
except Exception as e:
    storage_uri = "memory://"
    logger.info(f"Using in-memory storage for rate limiting (Redis not available: {e})")

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"],  # Default limit for all endpoints
    storage_uri=storage_uri
)

def get_user_id(request: Request) -> str:
    """
    Get user ID from request for user-based rate limiting
    Falls back to IP address if user not authenticated
    """
    # Try to get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        # Try Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
    
    if token:
        try:
            from app.utils.security import decode_token
            payload = decode_token(token)
            if payload and payload.get("sub"):
                return f"user:{payload.get('sub')}"
        except Exception as e:
            logger.debug(f"Could not get user from token: {e}")
    
    # Fallback to IP address
    return get_remote_address(request)

# Rate limit configurations
# Format: "count/period" where period can be: second, minute, hour, day
RATE_LIMITS = {
    "login": "5/15minutes",           # 5 login attempts per 15 minutes
    "register": "3/hour",              # 3 registrations per hour
    "password_reset": "3/hour",        # 3 password reset requests per hour
    "api_default": "100/minute",       # 100 API requests per minute
    "file_upload": "10/hour",          # 10 file uploads per hour
    "csv_import": "5/hour",            # 5 CSV imports per hour
}

def create_rate_limit_response(request: Request, exc: RateLimitExceeded):
    """
    Custom rate limit exceeded response
    Returns user-friendly error message with retry information
    """
    retry_after = exc.retry_after if hasattr(exc, 'retry_after') else 60
    
    # Log rate limit violation
    try:
        from app.database import SessionLocal
        from app.services.log_service import create_log
        from app.utils.request_utils import get_client_ip
        
        db = SessionLocal()
        try:
            ip_address = get_client_ip(request)
            create_log(
                db=db,
                level="WARNING",
                category="Security",
                action="Rate Limit Exceeded",
                message=f"Rate limit exceeded for IP: {ip_address}",
                ip_address=ip_address,
                status="Failed",
                details={
                    "endpoint": str(request.url.path),
                    "method": request.method,
                    "retry_after": retry_after
                }
            )
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error logging rate limit violation: {e}")
    
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after_seconds": retry_after,
            "error_code": "RATE_LIMIT_EXCEEDED"
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(exc.limit) if hasattr(exc, 'limit') else "unknown",
            "X-RateLimit-Remaining": "0"
        }
    )

