import json
import logging
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from fastapi.encoders import jsonable_encoder

from app.core.config import settings

logger = logging.getLogger(__name__)


class HistoricalDataCache:
    """Cache service for historical data queries."""

    def __init__(self):
        self.enabled = settings.USE_REDIS_CACHE
        self.ttl = settings.CACHE_TTL_DEFAULT

        # Initialize Redis connection
        try:
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
            logger.info("Redis cache initialized for historical data")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
            self.enabled = False
            self.redis = None

    def _generate_cache_key(
        self, instrument_id: int, period: str, interval: str
    ) -> str:
        """Generate a consistent cache key based on query parameters."""
        return f"historical:data:{instrument_id}:{period}:{interval}"

    async def get_cached_data(
        self, instrument_id: int, period: str, interval: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Try to get historical data from cache."""
        if not self.enabled or not self.redis:
            return None

        try:
            cache_key = self._generate_cache_key(instrument_id, period, interval)
            cached_data = await self.redis.get(cache_key)

            if not cached_data:
                return None

            # Parse JSON data from cache
            return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {e}")
            return None

    async def cache_data(
        self, instrument_id: int, period: str, interval: str, data: List[Any]
    ) -> bool:
        """Cache historical data with appropriate TTL."""
        if not self.enabled or not self.redis:
            return False

        try:
            cache_key = self._generate_cache_key(instrument_id, period, interval)

            # Serialize data to JSON, handling SQLAlchemy objects
            serialized_data = json.dumps(jsonable_encoder(data))

            # Set TTL based on interval (shorter intervals = shorter TTL)
            ttl = self._get_ttl_for_interval(interval)

            # Store in cache
            await self.redis.set(cache_key, serialized_data, ex=ttl)
            logger.debug(
                f"Cached historical data for {instrument_id} ({period}/{interval}) "
                f"for {ttl}s"
            )
            return True
        except Exception as e:
            logger.warning(f"Error caching data: {e}")
            return False

    async def invalidate_cache(self, instrument_id: Optional[int] = None) -> None:
        """Invalidate cache entries for a specific instrument or all instruments."""
        if not self.enabled or not self.redis:
            return

        try:
            if instrument_id is not None:
                # Invalidate cache for specific instrument
                pattern = f"historical:data:{instrument_id}:*"
            else:
                # Invalidate all historical data cache
                pattern = "historical:data:*"

            # Find all matching keys
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, pattern, 100)
                if keys:
                    await self.redis.delete(*keys)
                    logger.info(
                        f"Invalidated {len(keys)} cache entries with pattern {pattern}"
                    )
                if cursor == 0:
                    break
        except Exception as e:
            logger.warning(f"Error invalidating cache: {e}")

    def _get_ttl_for_interval(self, interval: str) -> int:
        """Return appropriate TTL based on the query interval."""
        # Shorter intervals expire faster since they update more frequently
        ttl_map = {
            "1m": 60,  # 1 minute data expires in 60s
            "5m": 5 * 60,  # 5 minute data expires in 5min
            "15m": 15 * 60,  # 15 minute data expires in 15min
            "30m": 30 * 60,  # 30 minute data expires in 30min
            "1h": 60 * 60,  # 1 hour data expires in 1h
            "1d": 6 * 60 * 60,  # 1 day data expires in 6h
            "1w": 24 * 60 * 60,  # 1 week data expires in 24h
        }
        return ttl_map.get(interval, self.ttl)


# Create singleton instance
historical_cache = HistoricalDataCache()
