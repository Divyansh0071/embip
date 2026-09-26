"""
Centralized Rate Limiting Module for EMBIP using slowapi.
Provides environment-driven storage (Memory vs. Redis), authenticated User ID key extraction,
and custom HTTP 429 response handling.
"""

import os
from typing import Optional
import jwt
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings


def get_remote_address_or_user_id(request: Request) -> str:
    """
    Key function for slowapi limiter.
    For authenticated requests with Bearer JWT: extracts user_id ('sub') -> 'user:<user_id>'.
    For unauthenticated requests: extracts client IP address -> 'ip:<client_ip>'.
    """
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        try:
            # Decode payload unverified here solely to extract 'sub' for rate limiting keying
            payload = jwt.decode(token, options={"verify_signature": False, "verify_exp": False}, algorithms=["HS256", "RS256"])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{str(user_id).strip()}"
        except Exception:
            pass

    # Fallback to Client IP address
    ip_addr = get_remote_address(request) or "127.0.0.1"
    return f"ip:{ip_addr}"


def get_storage_uri() -> str:
    """
    Returns storage URI for slowapi limiter.
    Defaults to memory storage ('memory://').
    Uses Redis storage if REDIS_URL environment variable is set.
    """
    redis_url = settings.REDIS_URL or os.getenv("REDIS_URL")
    if redis_url and (redis_url.startswith("redis://") or redis_url.startswith("rediss://")):
        return redis_url
    return "memory://"


# Global Limiter Instance
limiter = Limiter(
    key_func=get_remote_address_or_user_id,
    storage_uri=get_storage_uri(),
    enabled=settings.RATE_LIMIT_ENABLED,
)


def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom HTTP 429 response handler when rate limit is exceeded.
    Returns clean JSON payload and Retry-After HTTP header without exposing internal limiter state.
    """
    retry_after_seconds = 60
    headers = {"Retry-After": str(retry_after_seconds)}

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please wait before retrying.",
            "retry_after_seconds": retry_after_seconds,
        },
        headers=headers,
    )
