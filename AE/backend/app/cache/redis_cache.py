import json
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings


class RedisCache:
    def __init__(self):
        # Check for Redis URL first
        if settings.REDIS_URL:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        else:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
            )

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        data = await self.redis.get(key)
        if not data:
            return None
        return json.loads(data)

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set a value in cache with TTL in seconds"""
        return await self.redis.set(key, json.dumps(value), ex=ttl)
