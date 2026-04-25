"""
Redis integration for caching, rate limiting, and queueing.
"""

from __future__ import annotations


import redis.asyncio as aioredis
from typing import Optional

redis_client: Optional[aioredis.Redis] = None


async def init_redis(redis_url: str):
    """Initialize the global Redis connection pool. Fails gracefully."""
    global redis_client
    try:
        client = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await client.ping()
        redis_client = client
    except Exception:
        import logging

        logging.getLogger("behavedrift").warning(
            "Redis unavailable at %s — rate limiting disabled.", redis_url
        )
        redis_client = None


async def close_redis():
    """Close the global Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
