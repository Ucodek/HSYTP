import logging
from datetime import timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis
from redis.asyncio.client import Redis

from app.cache.base_cache import BaseCache
from app.core.config.base import settings

logger = logging.getLogger(__name__)


class RedisCache(BaseCache):
    """Redis-based cache implementation."""

    def __init__(self, client: Redis):
        """
        Initialize the Redis cache.

        Args:
            client: Redis client instance
        """
        self.client = client

    @classmethod
    async def create(
        cls,
        host: str = None,
        port: int = None,
        password: str = None,
        db: int = 0,
        prefix: str = "cache:",
    ) -> "RedisCache":
        """
        Create a new Redis cache instance.

        Args:
            host: Redis host
            port: Redis port
            password: Redis password
            db: Redis database
            prefix: Key prefix for all cache keys

        Returns:
            RedisCache instance
        """
        # Use settings if parameters not provided
        host = host or settings.REDIS_HOST
        port = port or settings.REDIS_PORT

        try:
            client = redis.Redis(
                host=host,
                port=port,
                password=password,
                db=db,
                decode_responses=False,  # We handle serialization ourselves
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )

            # Test connection
            await client.ping()

            logger.info(f"Connected to Redis at {host}:{port}")
            return cls(client)
        except Exception as e:
            logger.error(f"Failed to connect to Redis at {host}:{port}: {str(e)}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        try:
            value = await self.client.get(key)
            return self.deserialize(value) if value is not None else None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {str(e)}")
            return None

    async def set(
        self, key: str, value: Any, expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set a value in the cache."""
        try:
            serialized_value = self.serialize(value)

            if expire is None:
                return await self.client.set(key, serialized_value)
            elif isinstance(expire, timedelta):
                expire_seconds = int(expire.total_seconds())
                return await self.client.setex(key, expire_seconds, serialized_value)
            else:
                return await self.client.setex(key, expire, serialized_value)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        try:
            return await self.client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {str(e)}")
            return False

    async def clear(self) -> bool:
        """Clear all keys in the current Redis database."""
        try:
            await self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}")
            return False

    async def ttl(self, key: str) -> Optional[int]:
        """Get the time-to-live for a key in seconds."""
        try:
            ttl = await self.client.ttl(key)
            # Redis returns -1 if the key exists but has no expiry,
            # and -2 if the key doesn't exist
            return ttl if ttl >= 0 else None
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {str(e)}")
            return None

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in the cache."""
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis increment error for key {key}: {str(e)}")
            # If increment fails, try to initialize with the amount
            await self.set(key, amount)
            return amount

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a numeric value in the cache."""
        try:
            return await self.client.decrby(key, amount)
        except Exception as e:
            logger.error(f"Redis decrement error for key {key}: {str(e)}")
            # If decrement fails, try to initialize with negative amount
            await self.set(key, -amount)
            return -amount

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from the cache."""
        try:
            pipeline = self.client.pipeline()
            for key in keys:
                pipeline.get(key)

            results = await pipeline.execute()

            return {
                key: self.deserialize(value)
                for key, value in zip(keys, results)
                if value is not None
            }
        except Exception as e:
            logger.error(f"Redis get_many error: {str(e)}")
            return {}

    async def set_many(
        self, mapping: Dict[str, Any], expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set multiple values in the cache."""
        try:
            # Serialize all values
            serialized_mapping = {
                key: self.serialize(value) for key, value in mapping.items()
            }

            pipeline = self.client.pipeline()

            # Add all values to pipeline
            pipeline.mset(serialized_mapping)

            # Set expiry for each key if needed
            if expire is not None:
                expire_seconds = (
                    expire.total_seconds() if isinstance(expire, timedelta) else expire
                )
                for key in mapping:
                    pipeline.expire(key, expire_seconds)

            # Execute pipeline
            await pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Redis set_many error: {str(e)}")
            return False

    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from the cache."""
        if not keys:
            return 0

        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete_many error: {str(e)}")
            return 0


@lru_cache()
def get_redis_cache() -> Optional[RedisCache]:
    """
    Get or create a Redis cache instance.

    Returns:
        RedisCache instance or None if Redis is not available
    """
    if not settings.REDIS_HOST:
        logger.info("Redis host not configured, returning None")
        return None

    try:
        # Create a synchronous Redis client for simplicity
        import redis

        # Initialize Redis client with available settings
        # Note: Using getattr with default None for optional settings
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=getattr(
                settings, "REDIS_PASSWORD", None
            ),  # Use None if not defined
            db=getattr(settings, "REDIS_DB", 0),  # Default to DB 0 if not defined
            decode_responses=True,  # Changed to True for simpler string handling
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )

        # Test connection
        client.ping()

        # Create a sync-to-async wrapper for Redis operations
        class SyncRedisWrapper:
            def __init__(self, client):
                self.client = client

            # Implement required Redis operations synchronously
            def incr(self, key):
                return self.client.incr(key)

            def expire(self, key, seconds):
                return self.client.expire(key, seconds)

            def ttl(self, key):
                return self.client.ttl(key)

            def pipeline(self):
                return SyncPipelineWrapper(self.client.pipeline())

            def ping(self):
                return self.client.ping()

            def info(self, section=None):
                # Add the missing info method
                if section:
                    return self.client.info(section)
                return self.client.info()

            def get(self, key):
                return self.client.get(key)

            def set(self, key, value):
                return self.client.set(key, value)

            def setex(self, key, seconds, value):
                return self.client.setex(key, seconds, value)

            def delete(self, key):
                return self.client.delete(key)

            def exists(self, key):
                return self.client.exists(key)

            def flushdb(self):
                return self.client.flushdb()

            def mset(self, mapping):
                return self.client.mset(mapping)

        class SyncPipelineWrapper:
            def __init__(self, pipeline):
                self.pipeline = pipeline

            def incr(self, key):
                self.pipeline.incr(key)
                return self

            def ttl(self, key):
                self.pipeline.ttl(key)
                return self

            def expire(self, key, seconds):
                self.pipeline.expire(key, seconds)
                return self

            def execute(self):
                return self.pipeline.execute()

        logger.info(
            f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}"
        )
        return RedisCache(SyncRedisWrapper(client))
    except Exception as e:
        logger.error(f"Failed to create Redis cache: {str(e)}")
        return None
