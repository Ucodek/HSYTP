# Cache Component Documentation

This document provides a comprehensive overview of the Cache component in the backend_v2 application.

## Overview

The Cache component provides a flexible caching system with multiple implementations:
- Abstract base class defining consistent interface
- In-memory implementation for development and testing
- Redis implementation for production use
- Serialization and deserialization support
- TTL (time-to-live) management

## Directory Structure

```
app/cache/
├── __init__.py          # Package exports
├── base_cache.py        # Abstract base class
├── memory_cache.py      # In-memory implementation
└── redis_cache.py       # Redis implementation
```

## Core Components

### BaseCache

Abstract base class that defines the interface for all cache implementations:

```python
# Example: Base cache interface
class BaseCache(ABC, Generic[T]):
    @abstractmethod
    async def get(self, key: str) -> Optional[T]: ...
    
    @abstractmethod
    async def set(self, key: str, value: T, expire: Optional[Union[int, timedelta]] = None) -> bool: ...
    
    # Other abstract methods...
    
    # Concrete helper methods
    async def get_or_set(self, key: str, default_factory, expire=None) -> Any: ...
    def serialize(self, value: Any) -> bytes: ...
    def deserialize(self, value: bytes) -> Any: ...
```

Key features:
- Generic type parameter for type hinting
- Common data serialization/deserialization methods
- Utility methods for common operations

### MemoryCache

Simple in-memory cache implementation:

```python
# Example: Using the memory cache
cache = MemoryCache()
await cache.set("key", "value", expire=timedelta(minutes=10))
value = await cache.get("key")  # "value"
```

Key features:
- Thread-safe implementation with locks
- Automatic expiration of cached values
- No external dependencies
- Suitable for development and testing

### RedisCache

Redis-based cache implementation:

```python
# Example: Creating a Redis cache
redis_cache = await RedisCache.create(
    host="localhost",
    port=6379,
    password="secret",
    db=0,
    prefix="app:"
)

# Example: Using the Redis cache
await redis_cache.set("user:1", user_dict, expire=300)
user = await redis_cache.get("user:1")
```

Key features:
- Asynchronous Redis client
- Connection pooling
- Error handling with logging
- Automatic serialization

## Usage Patterns

### Basic Caching

```python
# Getting and setting values
value = await cache.get("my_key")
if value is None:
    # Value not in cache
    value = compute_expensive_value()
    await cache.set("my_key", value, expire=3600)  # Expire in 1 hour
```

### Get or Set Pattern

```python
# Using get_or_set for cleaner code
async def get_expensive_data():
    return compute_expensive_value()

value = await cache.get_or_set("my_key", get_expensive_data, expire=3600)
```

### Caching Multiple Values

```python
# Setting multiple values at once
items = {
    "user:1": user1,
    "user:2": user2,
    "user:3": user3
}
await cache.set_many(items, expire=timedelta(minutes=30))

# Getting multiple values
users = await cache.get_many(["user:1", "user:2", "user:3"])
```

### Counters and Rate Limiting

```python
# Using increment for counters
await cache.set("visits", 0)
await cache.increment("visits")  # 1
await cache.increment("visits", 10)  # 11

# Using for rate limiting
key = f"rate_limit:{user_id}"
count = await cache.increment(key)
await cache.expire(key, 60)  # Reset after 60 seconds
if count > 10:
    raise RateLimitExceeded()
```

## Implementation in Services

### Dependency Injection for Cache

```python
# In a service module
class UserService:
    def __init__(self, cache: BaseCache):
        self.cache = cache
        self.cache_prefix = "user:"
        
    async def get_user(self, user_id: int) -> Optional[User]:
        # Try to get from cache first
        cache_key = f"{self.cache_prefix}{user_id}"
        user_data = await self.cache.get(cache_key)
        
        if user_data:
            return User(**user_data)
            
        # Not in cache, get from database
        user = await self.db.get_user(user_id)
        if user:
            # Cache for future requests
            await self.cache.set(
                cache_key, 
                user.model_dump(), 
                expire=timedelta(minutes=30)
            )
        
        return user
```

### Using Cache Factory

```python
# Getting the appropriate cache implementation
from app.cache import get_redis_cache, MemoryCache

async def get_cache() -> BaseCache:
    # Try to get Redis cache first
    redis_cache = get_redis_cache()
    if redis_cache:
        return redis_cache
    
    # Fall back to memory cache if Redis is not available
    return MemoryCache()
```

## Best Practices

1. **Appropriate Cache Keys:**
   - Use consistent naming conventions
   - Include type or domain in key names (e.g., "user:123", "product:456")
   - Consider adding version numbers for schema changes

2. **Cache Invalidation:**
   - Set reasonable expiration times
   - Explicitly delete related cache entries when data changes
   - Use prefixes to enable batch invalidation

3. **Error Handling:**
   - Treat cache failures as non-fatal
   - Always have a fallback when cache is unavailable
   - Log cache errors but don't propagate them to users

4. **Cache Serialization:**
   - Store simple serializable data when possible (dictionaries, not objects)
   - If storing complex objects, ensure they can be properly serialized
   - Handle serialization exceptions gracefully

5. **Performance Considerations:**
   - Cache expensive operations, not simple database lookups
   - Consider the trade-offs between memory usage and performance
   - Monitor hit/miss rates to evaluate effectiveness

## Implementation Notes

1. **Choosing Cache Implementation:**
   - Development/Testing: MemoryCache
   - Production: RedisCache
   - Unit tests: Mock implementations

2. **Cache Keys Design:**
   - `<entity_type>:<id>` for individual objects
   - `<entity_type>:list:<params>` for lists of objects
   - `<service>:<function>:<params>` for function results

3. **Data Serialization:**
   - Default serialization uses JSON for efficiency
   - Falls back to pickle for complex objects
   - Custom serialization can be implemented if needed
