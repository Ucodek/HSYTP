import threading
import time
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from app.cache.base_cache import BaseCache


class MemoryCache(BaseCache):
    """Simple in-memory cache implementation for development and testing."""

    def __init__(self):
        """Initialize the memory cache."""
        self._cache: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._lock = threading.RLock()

    def _is_expired(self, key: str) -> bool:
        """Check if a key is expired."""
        _, expiry = self._cache.get(key, (None, None))
        if expiry is None:
            return False
        return expiry < time.time()

    def _clean_expired(self):
        """Remove all expired keys."""
        now = time.time()
        with self._lock:
            expired_keys = [
                key
                for key, (_, expiry) in self._cache.items()
                if expiry is not None and expiry < now
            ]
            for key in expired_keys:
                del self._cache[key]

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        with self._lock:
            if key not in self._cache:
                return None

            if self._is_expired(key):
                del self._cache[key]
                return None

            value, _ = self._cache[key]
            return value

    async def set(
        self, key: str, value: Any, expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set a value in the cache."""
        expiry = None
        if expire is not None:
            if isinstance(expire, timedelta):
                expire_seconds = expire.total_seconds()
            else:
                expire_seconds = expire
            expiry = time.time() + expire_seconds

        with self._lock:
            self._cache[key] = (value, expiry)
            self._clean_expired()
        return True

    async def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        with self._lock:
            if key not in self._cache:
                return False

            if self._is_expired(key):
                del self._cache[key]
                return False

            return True

    async def clear(self) -> bool:
        """Clear all values from the cache."""
        with self._lock:
            self._cache.clear()
        return True

    async def ttl(self, key: str) -> Optional[int]:
        """Get the time-to-live for a key in seconds."""
        with self._lock:
            if key not in self._cache:
                return None

            _, expiry = self._cache[key]
            if expiry is None:
                return None

            remaining = expiry - time.time()
            if remaining <= 0:
                del self._cache[key]
                return None

            return int(remaining)

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in the cache."""
        with self._lock:
            if key not in self._cache:
                self._cache[key] = (amount, None)
                return amount

            if self._is_expired(key):
                self._cache[key] = (amount, None)
                return amount

            value, expiry = self._cache[key]
            if not isinstance(value, (int, float)):
                value = 0

            new_value = value + amount
            self._cache[key] = (new_value, expiry)
            return new_value

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a numeric value in the cache."""
        return await self.increment(key, -amount)

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from the cache."""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result

    async def set_many(
        self, mapping: Dict[str, Any], expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set multiple values in the cache."""
        for key, value in mapping.items():
            await self.set(key, value, expire)
        return True

    async def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from the cache."""
        count = 0
        for key in keys:
            if await self.delete(key):
                count += 1
        return count
