import json
import pickle
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")


class BaseCache(ABC, Generic[T]):
    """Abstract base class for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[T]:
        """
        Retrieve a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value or None if the key doesn't exist
        """

    @abstractmethod
    async def set(
        self, key: str, value: T, expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """
        Store a value in the cache.

        Args:
            key: The cache key
            value: The value to store
            expire: Optional expiration time in seconds or as timedelta

        Returns:
            True if the value was stored successfully
        """

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Remove a value from the cache.

        Args:
            key: The cache key

        Returns:
            True if the key was deleted, False if it didn't exist
        """

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: The cache key

        Returns:
            True if the key exists, False otherwise
        """

    @abstractmethod
    async def clear(self) -> bool:
        """
        Clear all values from the cache.

        Returns:
            True if the cache was cleared successfully
        """

    @abstractmethod
    async def ttl(self, key: str) -> Optional[int]:
        """
        Get the time-to-live for a key in seconds.

        Args:
            key: The cache key

        Returns:
            Time-to-live in seconds, None if the key doesn't exist
            or if it doesn't have an expiration
        """

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a numeric value in the cache.

        Args:
            key: The cache key
            amount: The amount to increment by

        Returns:
            The new value
        """

    @abstractmethod
    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrement a numeric value in the cache.

        Args:
            key: The cache key
            amount: The amount to decrement by

        Returns:
            The new value
        """

    @abstractmethod
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Retrieve multiple values from the cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary mapping keys to their values
        """

    @abstractmethod
    async def set_many(
        self, mapping: Dict[str, Any], expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """
        Store multiple values in the cache.

        Args:
            mapping: Dictionary mapping keys to values
            expire: Optional expiration time in seconds or as timedelta

        Returns:
            True if all values were stored successfully
        """

    @abstractmethod
    async def delete_many(self, keys: List[str]) -> int:
        """
        Remove multiple values from the cache.

        Args:
            keys: List of cache keys

        Returns:
            Number of keys that were deleted
        """

    async def get_or_set(
        self, key: str, default_factory, expire: Optional[Union[int, timedelta]] = None
    ) -> Any:
        """
        Retrieve a value from the cache or set it if it doesn't exist.

        Args:
            key: The cache key
            default_factory: Function to call to get the default value
            expire: Optional expiration time in seconds or as timedelta

        Returns:
            The cached value
        """
        value = await self.get(key)
        if value is None:
            value = await default_factory()
            await self.set(key, value, expire)
        return value

    def serialize(self, value: Any) -> bytes:
        """
        Serialize a value for storage.

        Args:
            value: The value to serialize

        Returns:
            Serialized value as bytes
        """
        try:
            # Try JSON serialization first (more compact)
            return json.dumps(value).encode("utf-8")
        except (TypeError, ValueError):
            # Fall back to pickle for non-JSON-serializable objects
            return pickle.dumps(value)

    def deserialize(self, value: bytes) -> Any:
        """
        Deserialize a value from storage.

        Args:
            value: The value to deserialize

        Returns:
            Deserialized value
        """
        if value is None:
            return None

        try:
            # Try JSON deserialization first
            return json.loads(value.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            try:
                return pickle.loads(value)
            except pickle.PickleError:
                # If all deserialization fails, return the raw value
                return value
