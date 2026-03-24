"""
Redis integration for caching, rate limiting, and queueing.
"""

import redis.asyncio as aioredis
from typing import Optional

redis_client: Optional[aioredis.Redis] = None

async def init_redis(redis_url: str):
    """Initialize the global Redis connection pool."""
    global redis_client
    redis_client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)

async def close_redis():
    """Close the global Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
