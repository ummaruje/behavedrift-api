"""
Rate Limiting Middleware using Redis
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import redis
from app.config import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting if Redis isn't initialized
        if not redis.redis_client:
            return await call_next(request)

        # Skip health check endpoint from rate limiting
        if request.url.path == "/health":
            return await call_next(request)

        # Identify the client by API Key, Token tail, or IP Address
        identifier = request.client.host if request.client else "unknown"
        if "x-api-key" in request.headers:
            identifier = request.headers["x-api-key"][:16]
        elif "authorization" in request.headers:
            identifier = request.headers["authorization"][-16:]

        # Very simple fixed-window rate limiting using current minute timestamp
        current_minute = int(time.time() / 60)
        key = f"rate_limit:{identifier}:{current_minute}"

        try:
            current_count = await redis.redis_client.incr(key)
            if current_count == 1:
                # Expire the key safely after the window passes
                await redis.redis_client.expire(key, 60)

            if current_count > settings.rate_limit_requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Too many requests. Limit is {settings.rate_limit_requests_per_minute} per minute.",
                        }
                    },
                )
        except Exception:
            # If Redis goes down, fail open (allow requests but don't rate limit)
            pass

        return await call_next(request)
