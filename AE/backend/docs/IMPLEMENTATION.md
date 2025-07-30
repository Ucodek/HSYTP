# Financial Data API - Implementation Guide

## Concrete Project Structure

Below is the exact file and folder structure you'll have after implementing the Financial Data API according to our design:

```
financial-api/
│
├── app/
│   ├── __init__.py                                 # Package marker
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                                 # Shared API dependencies
│   │   │
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py                           # Combines all API routers
│   │       │
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── instruments.py                  # /instruments/* endpoints
│   │           ├── market.py                       # /market/* endpoints
│   │           ├── news.py                         # /news endpoints
│   │           ├── posts.py                        # /posts endpoints
│   │           ├── events.py                       # /events endpoints
│   │           ├── portfolio.py                    # /portfolio/* endpoints
│   │           ├── search.py                       # /search endpoint
│   │           └── users.py                        # Authentication endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                              # Environment-based configuration
│   │   ├── security.py                            # JWT, password hashing
│   │   ├── errors.py                              # Custom exceptions
│   │   └── monitoring.py                          # Monitoring setup
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                                # SQLAlchemy base setup
│   │   ├── session.py                             # DB connection handling
│   │   ├── init_db.py                             # DB initialization
│   │   └── versioning.py                          # Schema version management
│   │
│   ├── models/                                    # SQLAlchemy models
│   │   ├── __init__.py                            # Imports all models
│   │   ├── base.py                                # Base model class
│   │   ├── instruments.py                         # Instrument, InstrumentPrice
│   │   ├── market.py                              # MarketIndex, MarketIndexPrice
│   │   ├── news.py                                # News model
│   │   ├── posts.py                               # Post model
│   │   ├── events.py                              # EconomicEvent model
│   │   ├── portfolio.py                           # Portfolio, PortfolioAsset
│   │   └── users.py                               # User, RefreshToken models
│   │
│   ├── schemas/                                   # Pydantic models
│   │   ├── __init__.py
│   │   ├── base.py                                # Base schemas
│   │   ├── instruments.py                         # InstrumentCreate, InstrumentResponse
│   │   ├── market.py                              # MarketIndexResponse
│   │   ├── news.py                                # NewsArticleResponse
│   │   ├── posts.py                               # PostResponse
│   │   ├── events.py                              # EconomicEventResponse
│   │   ├── portfolio.py                           # PortfolioCreate, OptimizationRequest
│   │   └── users.py                               # UserCreate, Token schemas
│   │
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py                                # Generic CRUD operations
│   │   ├── instruments.py                         # Instrument CRUD operations
│   │   ├── market.py                              # Market CRUD operations
│   │   ├── news.py                                # News CRUD operations
│   │   ├── posts.py                               # Post CRUD operations
│   │   ├── events.py                              # Event CRUD operations
│   │   ├── portfolio.py                           # Portfolio CRUD operations
│   │   └── users.py                               # User CRUD operations
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── instruments_service.py                 # Instrument business logic
│   │   ├── market_service.py                      # Market data business logic
│   │   ├── news_service.py                        # News business logic
│   │   ├── posts_service.py                       # Posts business logic
│   │   ├── events_service.py                      # Economic events business logic
│   │   ├── portfolio_service.py                   # Portfolio management
│   │   ├── optimization_service.py                # Portfolio optimization
│   │   ├── search_service.py                      # Search functionality
│   │   └── user_service.py                        # User management
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── base_client.py                         # Base API client
│   │   ├── alpha_vantage.py                       # Alpha Vantage integration
│   │   ├── yahoo_finance.py                       # Yahoo Finance integration
│   │   ├── news_api.py                            # News API integration
│   │   └── trading_economics.py                   # Trading Economics API
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── worker.py                              # Celery configuration
│   │   ├── market_data.py                         # Market data update tasks
│   │   ├── historical_data.py                     # Historical data collection
│   │   └── scheduled.py                           # Scheduled task definitions
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── i18n.py                                # Internationalization helpers
│   │   ├── time_utils.py                          # Date/time utilities
│   │   └── validators.py                          # Custom validators
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── logging.py                             # Logging middleware
│   │   └── rate_limiting.py                       # Rate limiting middleware
│   │
│   └── cache/
│       ├── __init__.py
│       ├── redis_cache.py                         # Redis cache implementation
│       └── cache_keys.py                          # Cache key generation
│
├── migrations/                                    # Alembic migrations
│   ├── __init__.py
│   ├── versions/
│   │   ├── __init__.py
│   │   ├── 001_create_users_table.py
│   │   ├── 002_create_instruments_table.py
│   │   └── ...other migration scripts...
│   ├── env.py                                     # Alembic environment
│   └── script.py.mako                             # Migration script template
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                                # Test fixtures
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_instruments.py                    # Instrument API tests
│   │   ├── test_market.py                         # Market API tests
│   │   ├── test_news.py                           # News API tests
│   │   ├── test_posts.py                          # Posts API tests
│   │   ├── test_events.py                         # Events API tests
│   │   ├── test_portfolio.py                      # Portfolio API tests
│   │   └── test_search.py                         # Search API tests
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── test_instruments_service.py
│   │   ├── test_market_service.py
│   │   └── ...other service tests...
│   │
│   └── utils/
│       ├── __init__.py
│       ├── test_i18n.py
│       └── test_time_utils.py
│
├── scripts/
│   ├── seed_db.py                                 # Database seeding script
│   ├── generate_keys.py                           # Generate security keys
│   └── create_migration.py                        # Migration creation helper
│
├── docker/
│   ├── Dockerfile                                 # Production Dockerfile
│   ├── Dockerfile.dev                             # Development Dockerfile
│   └── entrypoint.sh                              # Docker entrypoint script
│
├── .env.example                                   # Example environment variables
├── .gitignore                                     # Git ignore file
├── alembic.ini                                    # Alembic configuration
├── docker-compose.yml                             # Production compose file
├── docker-compose.dev.yml                         # Development compose file
├── main.py                                        # Application entry point
├── pyproject.toml                                 # Poetry dependencies
├── poetry.lock                                    # Locked dependencies
└── README.md                                      # Project documentation
```

## Best Practices

### 1. Code Organization

- Keep endpoint handlers thin - move business logic to services
- Use dependency injection for components
- Follow single responsibility principle

### 2. Error Handling

- Use custom exceptions that map to HTTP error codes
- Include error codes that can be translated to user-friendly messages on frontend
- Log detailed error information but return sanitized messages to clients
- Implement global exception handlers to ensure consistent error responses

```python
# Example global exception handler
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )

# Example usage in service
async def get_instrument_by_symbol(self, db: AsyncSession, symbol: str):
    instrument = await self.instruments_crud.get_by_symbol(db, symbol)
    if not instrument:
        raise ResourceNotFoundError(resource="instrument", id_value=symbol)
    return instrument
```

### 3. Database Access Patterns

- Use async database operations throughout the application
- Implement unit-of-work pattern with transaction management
- Batch operations where possible to reduce database round-trips
- Use connection pooling for better performance

```python
# Example transaction pattern
async def create_portfolio_with_assets(
    self, db: AsyncSession, user_id: int, portfolio_data: dict, assets: List[dict]
):
    async with db.begin():
        # Create portfolio
        portfolio = await self.portfolios_crud.create(
            db, obj_in=PortfolioCreate(**portfolio_data, user_id=user_id)
        )

        # Add assets in same transaction
        for asset in assets:
            await self.portfolio_assets_crud.create(
                db,
                obj_in=PortfolioAssetCreate(
                    portfolio_id=portfolio.id,
                    **asset
                )
            )

        return portfolio
```

### 4. Caching Strategy

- Use function-level caching for expensive operations
- Implement cache invalidation on data updates
- Use staggered cache expiration to prevent cache stampedes
- Store complex objects as JSON for quick serialization/deserialization

```python
# Example caching decorator
def cached(ttl: int = 300, prefix: str = "cache"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate unique cache key
            key_parts = [prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            key = ":".join(key_parts)

            # Try to get from cache
            cached_result = await redis_cache.get(key)
            if cached_result:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

# Usage example
@cached(ttl=600, prefix="instrument")
async def get_instrument_with_price(self, db: AsyncSession, symbol: str):
    # Implementation
```

### 5. Logging Practices

- Use structured logging with context
- Include correlation IDs for request tracing
- Log enough information for debugging without exposing sensitive data
- Use different log levels appropriately (DEBUG, INFO, WARNING, ERROR)

```python
# Example structured logging
logger.info(
    "Portfolio optimization completed",
    extra={
        "user_id": user_id,
        "portfolio_id": portfolio_id,
        "strategy": strategy,
        "duration_ms": execution_time,
        "correlation_id": correlation_id
    }
)
```

## Data Validation Strategy

Data validation is critical for a financial application to ensure data integrity, security, and proper behavior. Our implementation uses a multi-layered validation approach:

### 1. Request Validation with Pydantic

FastAPI with Pydantic provides automatic request validation:

```python
# filepath: financial-api/app/schemas/instruments.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
from datetime import datetime

class InstrumentType(str, Enum):
    STOCK = "stock"
    INDEX = "index"
    CRYPTO = "crypto"
    ETF = "etf"

class InstrumentCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, description="Instrument symbol")
    name: dict = Field(..., description="Multilingual instrument name")
    type: InstrumentType
    country: Optional[str] = Field(None, min_length=2, max_length=3, description="Country code")
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="Currency code")

    # Custom validator for symbol format
    @validator('symbol')
    def symbol_must_be_valid(cls, v):
        if not v.isalnum() and not '-' in v and not '.' in v:
            raise ValueError('Symbol must contain only alphanumeric characters, hyphens, or periods')
        return v.upper()  # Normalize to uppercase

    # Custom validator for multilingual name
    @validator('name')
    def validate_name(cls, v):
        if not isinstance(v, dict) or not v:
            raise ValueError('Name must be a non-empty dictionary with language codes')

        # Ensure at least one language is provided
        if not any(v.values()):
            raise ValueError('At least one language translation must be provided')

        # Ensure English name exists
        if 'en-US' not in v or not v['en-US']:
            raise ValueError('English (en-US) name must be provided')

        return v
```

### 2. Financial Data-Specific Validation

Financial data often requires specialized validation:

```python
# filepath: financial-api/app/utils/validators.py
from pydantic import validator
from decimal import Decimal
import re

def validate_price(price: Decimal) -> Decimal:
    """Validate that price is non-negative and has proper precision"""
    if price < 0:
        raise ValueError("Price cannot be negative")

    # Maximum 4 decimal places for standard prices
    if price.as_tuple().exponent < -4:
        raise ValueError("Price cannot have more than 4 decimal places")

    return price

def validate_percentage(value: float) -> float:
    """Validate percentage values"""
    if value < -100 or value > 100:
        raise ValueError("Percentage must be between -100 and 100")
    return value

def validate_ticker_symbol(symbol: str) -> str:
    """Validate stock ticker symbol format"""
    # Basic pattern for most exchanges
    pattern = r'^[A-Z0-9.-]{1,20}$'
    if not re.match(pattern, symbol):
        raise ValueError("Invalid ticker symbol format")
    return symbol
```

### 3. Domain Validation in Services

Service layer implements business rule validations:

```python
# filepath: financial-api/app/services/portfolio_service.py
from app.schemas.portfolio import PortfolioCreate
from app.utils.validators import validate_percentage

class PortfolioService:
    async def create_portfolio(self, db: AsyncSession, user_id: int, data: PortfolioCreate):
        """Create a new portfolio with validation"""

        # Validate that portfolio allocations sum to 100%
        total_allocation = sum(asset.allocation for asset in data.assets)
        if abs(total_allocation - 1.0) > 0.0001:  # Allow small rounding errors
            raise ValueError("Portfolio allocations must sum to 100%")

        # Validate that all referenced instruments exist
        instrument_symbols = [asset.symbol for asset in data.assets]
        existing_instruments = await self.instruments_crud.get_by_symbols(db, instrument_symbols)

        if len(existing_instruments) != len(instrument_symbols):
            existing_symbols = {i.symbol for i in existing_instruments}
            missing = set(instrument_symbols) - existing_symbols
            raise ValueError(f"Instruments not found: {', '.join(missing)}")

        # Proceed with creation
        # ...implementation...
```

### 4. Database Constraints

SQL constraints provide the final validation layer:

```sql
-- filepath: financial-api/migrations/versions/xxx_add_constraints.py
"""Add database constraints for validation

Revision ID: xxx
"""

def upgrade():
    op.create_check_constraint(
        "ck_positive_price",
        "instrument_prices",
        "price >= 0"
    )

    op.create_check_constraint(
        "ck_portfolio_allocation",
        "portfolio_assets",
        "allocation > 0 AND allocation <= 1"
    )

    op.create_check_constraint(
        "ck_valid_percent",
        "instrument_prices",
        "change_percent >= -100 AND change_percent <= 100"
    )
```

### 5. Validation Error Handling

Centralized error handling for validation errors:

```python
# filepath: financial-api/app/core/errors.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI request validation errors"""
    errors = []
    for error in exc.errors():
        error_msg = {
            "field": error["loc"][-1] if error["loc"] else None,
            "msg": error["msg"],
            "type": error["type"]
        }
        errors.append(error_msg)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": errors
            }
        }
    )

# In main.py:
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
```

### 6. Advanced Validation Techniques

#### Contextual Validation

Some validation rules depend on the context of the operation:

```python
# filepath: financial-api/app/services/market_service.py
class MarketService:
    async def validate_trading_hours(self, symbol: str, market_type: str):
        """Validate that operation is within trading hours"""
        # Get market trading hours
        market_info = self.market_config.get(market_type)
        if not market_info:
            return True  # Unknown market, skip validation

        # Check current time against trading hours
        now = datetime.now(tz=pytz.timezone(market_info["timezone"]))

        # Convert market open/close times to current date
        today_open = datetime.combine(now.date(), market_info["open_time"])
        today_close = datetime.combine(now.date(), market_info["close_time"])

        # Add timezone info
        today_open = pytz.timezone(market_info["timezone"]).localize(today_open)
        today_close = pytz.timezone(market_info["timezone"]).localize(today_close)

        # Check if within trading hours
        if now < today_open or now > today_close:
            if market_info.get("allow_after_hours", False):
                # Allow operation but flag as after-hours
                return "after_hours"
            # Outside trading hours and after-hours not allowed
            raise ValueError(f"Market is closed for {symbol}")

        return True
```

#### Validation with Dependencies

Use FastAPI dependencies for request-level validation:

```python
# filepath: financial-api/app/api/deps.py
from fastapi import Depends, HTTPException, Query
from typing import Optional

async def validate_pagination(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> tuple:
    """Validate and return pagination parameters"""
    return limit, offset

async def validate_date_range(
    from_date: Optional[str] = Query(None, regex=r'^\d{4}-\d{2}-\d{2}$'),
    to_date: Optional[str] = Query(None, regex=r'^\d{4}-\d{2}-\d{2}$'),
) -> tuple:
    """Validate date range parameters"""
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_DATE_RANGE", "message": "From date cannot be after to date"}
        )

    return from_date, to_date

# Usage in endpoint
@router.get("/historical")
async def get_historical_data(
    symbol: str,
    pagination: tuple = Depends(validate_pagination),
    date_range: tuple = Depends(validate_date_range),
):
    limit, offset = pagination
    from_date, to_date = date_range
    # ...implementation...
```

### 7. Testing Validation Logic

Thorough testing of validation logic is essential:

```python
# filepath: financial-api/tests/utils/test_validators.py
import pytest
from decimal import Decimal
from app.utils.validators import validate_price, validate_percentage, validate_ticker_symbol

def test_price_validation():
    # Valid cases
    assert validate_price(Decimal('10.5')) == Decimal('10.5')
    assert validate_price(Decimal('0.0001')) == Decimal('0.0001')

    # Invalid cases
    with pytest.raises(ValueError, match="Price cannot be negative"):
        validate_price(Decimal('-1.0'))

    with pytest.raises(ValueError, match="Price cannot have more than 4 decimal places"):
        validate_price(Decimal('10.12345'))

# Additional tests for other validators...
```

## Getting Started

### 1. Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd financial-api

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Setup poetry environment
poetry install

# Start services with Docker Compose
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python -m scripts.seed_db

# Run the application
uvicorn main:app --reload
```

### 2. Running Tests

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/api/test_instruments.py

# Run with coverage
pytest --cov=app
```

### 3. Adding a New Feature

1. **Define requirements** based on the PRD
2. **Update database schema** if needed and create migrations
3. **Implement CRUD operations** for any new data entities
4. **Create service layer** with business logic
5. **Add API endpoints** that use the service layer
6. **Write tests** covering the new functionality
7. **Update documentation** (API docs, comments)

## Common Implementation Patterns

### 1. Implementing a New Endpoint with Caching

```python
# app/api/v1/endpoints/instruments.py
@router.get("/gainers", response_model=List[InstrumentResponse])
async def get_gainers(
    limit: int = Query(5, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    market_service: MarketService = Depends(get_market_service),
    current_user = Depends(get_current_user),
):
    """Get top gaining instruments."""
    cache_key = market_movers_key("gainers", limit=limit)

    # Try to get from cache first
    cached_data = await redis_cache.get(cache_key)
    if cached_data and settings.USE_REDIS_CACHE:
        return cached_data

    # Get from service if not in cache
    gainers = await market_service.get_top_gainers(db, limit=limit)

    # Cache the result
    if settings.USE_REDIS_CACHE:
        await redis_cache.set(
            cache_key,
            gainers,
            ttl=settings.CACHE_TTL_MARKET_MOVERS
        )

    return gainers
```

### 2. Multilingual Content Handling

```python
# app/services/news_service.py
async def get_news_articles(
    self,
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    language: str = "en-US"
):
    """Get news articles with proper localization."""
    articles = await self.news_crud.get_multi(
        db, limit=limit, offset=offset
    )

    # Transform to response format with proper i18n
    result = []
    for article in articles:
        result.append({
            "timestamp": article.timestamp,
            "title": get_translated_content(article.title, language),
            "source": article.source,
            "url": article.url,
            "summary": get_translated_content(article.summary, language),
            "cover": article.cover
        })

    return result
```

### 3. Implementing External API Client with Retries

```python
# app/clients/base_client.py - Enhanced version with retries
import httpx
import asyncio
from typing import Dict, Any, Optional
from app.core.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

class BaseApiClient:
    # ... existing code ...

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request with retry logic."""
        try:
            return await self._request(method, endpoint, params, data, headers)
        except httpx.HTTPStatusError as e:
            # Don't retry on certain status codes
            if e.response.status_code in (401, 403, 404):
                raise
            raise  # Let tenacity handle the retry
```

## Enhanced Implementation Guidelines

### 1. Tier-Based Rate Limiting Implementation

To implement the basic/premium tier rate limiting requirements from the PRD:

```python
# filepath: financial-api/app/middleware/rate_limiting.py
import time
from fastapi import Request, Response, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.users import User
from app.api.deps import get_current_user
from app.core.config import settings

async def rate_limit_middleware(
    request: Request,
    call_next,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get user's tier
    tier = current_user.subscription_tier

    # Set limits based on tier
    if (tier == "premium"):
        limit = settings.RATE_LIMIT_PREMIUM
    else:
        limit = settings.RATE_LIMIT_BASIC

    # Check current rate using Redis
    key = f"rate_limit:{current_user.id}:{request.url.path}"
    window = int(time.time() / 60)  # 1-minute window
    window_key = f"{key}:{window}"

    # Increment counter for this window
    current_count = await request.app.redis.incr(window_key)

    # Set expiry if this is the first request in the window
    if current_count == 1:
        await request.app.redis.expire(window_key, 60)

    # Check if over limit
    if current_count > limit:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded. Please try again later."
                }
            }
        )

    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-Rate-Limit-Limit"] = str(limit)
    response.headers["X-Rate-Limit-Remaining"] = str(max(0, limit - current_count))
    response.headers["X-Rate-Limit-Reset"] = str((window + 1) * 60)

    return response

# Registration in main.py
app.middleware("http")(rate_limit_middleware)
```

### 2. Monitoring Service Recommendation

Based on the project's requirements, we recommend **Datadog** as the primary monitoring solution for the following reasons:

```python
# filepath: financial-api/app/core/monitoring.py
from fastapi import FastAPI
import ddtrace.profiling.auto  # Datadog profiling
from ddtrace import patch, tracer  # Datadog tracing
from app.core.config import settings

def setup_monitoring(app: FastAPI):
    """Setup Datadog APM monitoring for the application"""

    # Configure Datadog tracer
    tracer.configure(
        service_name=settings.PROJECT_NAME,
        env=settings.ENVIRONMENT
    )

    # Patch common libraries
    patch(fastapi=True, sqlalchemy=True, redis=True, httpx=True)

    # Add instrumentation middleware
    @app.middleware("http")
    async def datadog_middleware(request, call_next):
        with tracer.trace("http_request", service=settings.PROJECT_NAME) as span:
            span.set_tag("endpoint", request.url.path)
            span.set_tag("method", request.method)

            response = await call_next(request)

            span.set_tag("status_code", response.status_code)
            return response

    return app
```

**Implementation in `main.py`:**

```python
# filepath: financial-api/main.py
from app.core.monitoring import setup_monitoring

# Initialize FastAPI
app = FastAPI(...)

# Setup monitoring (before adding routes)
setup_monitoring(app)
```

### 3. Database Schema Versioning Strategy

Add a dedicated file for schema versioning philosophy:

```python
# filepath: financial-api/app/db/versioning.py
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.ext.asyncio import AsyncConnection
from app.core.config import settings

class SchemaManager:
    """
    Manages database schema versioning strategy.
    Implements our zero-downtime migration approach.
    """

    @staticmethod
    async def is_compatible(conn: AsyncConnection, min_version: str) -> bool:
        """Check if the current schema version is compatible with the app"""
        context = MigrationContext.configure(conn)
        current_rev = context.get_current_revision()
        # Logic to check if current_rev is compatible with min_version
        return True  # Simplified for example

    @staticmethod
    async def get_current_version(conn: AsyncConnection) -> str:
        """Get the current schema version"""
        context = MigrationContext.configure(conn)
        return context.get_current_revision()

    @staticmethod
    async def run_online_migrations(conn: AsyncConnection) -> bool:
        """Run migrations that can be performed without downtime"""
        context = MigrationContext.configure(conn)
        op = Operations(context)

        # Example of online schema change that's backward compatible
        # - Adding a nullable column
        # - Creating a new index concurrently
        # - Adding a new table

        # These changes should be implemented in alembic migrations
        # with a clear indication that they are zero-downtime safe

        return True
```

**Implementation in application startup:**

```python
# filepath: financial-api/app/api/deps.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.versioning import SchemaManager

async def get_db_with_version_check() -> AsyncSession:
    """DB dependency that ensures schema compatibility"""
    async for db in get_db():
        async with db.connection() as conn:
            # Check if schema version is compatible
            if not await SchemaManager.is_compatible(conn, "1.0.0"):
                raise Exception("Database schema version is not compatible")
        yield db
```

### 4. File Path Consistency

For clarity and consistency with the project structure document, all code examples should use the full project paths:

```python
# filepath: financial-api/app/services/instruments_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

class InstrumentsService:
    # ...implementation...
```

## Development Workflow with Docker

To ensure consistent environment across all developers:

```bash
# Start the development environment
docker-compose -f docker-compose.dev.yml up -d

# Run migrations in Docker environment
docker-compose exec api alembic upgrade head

# Enter the container for debugging
docker-compose exec api bash

# Run tests inside the container
docker-compose exec api pytest
```

Docker Compose development file:

```yaml
# filepath: financial-api/docker-compose.dev.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - 8000:8000
    volumes:
      - .:/app
    depends_on:
      - postgres
      - redis
    environment:
      - POSTGRES_SERVER=postgres
      - REDIS_HOST=redis
      - ENVIRONMENT=development
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: timescale/timescaledb:latest-pg14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=financial_data
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  postgres-data:
  redis-data:
```

## Troubleshooting Guide

### 1. Database Connection Issues

**Symptoms:**
- `ConnectionRefusedError` or `CannotConnectNow` exceptions
- API hangs when trying to access database

**Solutions:**
- Check that PostgreSQL is running (`docker ps`)
- Verify connection string in `.env` file
- Try connecting with a direct client like `psql`
- Check for network issues between API and database

### 2. Cache Inconsistency

**Symptoms:**
- Stale data being returned
- Changes not reflecting immediately

**Solutions:**
- Implement cache invalidation patterns
- Add cache buster parameters for debugging
- Check Redis connection and memory usage
- Use cache warming for critical data

### 3. API Performance Issues

**Symptoms:**
- Slow response times
- Timeouts on complex queries

**Solutions:**
- Add SQL query logging and analyze slow queries
- Check for N+1 query problems
- Add indexing for frequently accessed fields
- Implement pagination and limit data fetching

## Monitoring Production Deployment

### 1. Health Checks

Implement health check endpoints:

```python
@app.get("/health")
async def health_check():
    """Simple health check."""
    return {"status": "ok"}

@app.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db)
):
    """Detailed health check with dependencies."""
    checks = {
        "api": "ok",
        "database": "checking",
        "redis": "checking"
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"

    # Check Redis
    try:
        await redis_cache.redis.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    return {"status": "ok" if all(v == "ok" for v in checks.values()) else "error", "checks": checks}
```

### 2. Performance Metrics

Use middleware to collect performance data:

```python
@app.middleware("http")
async def add_performance_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)

    # Log timing metrics
    logger.info(
        f"Request processed: {request.method} {request.url.path}",
        extra={
            "duration": process_time,
            "status_code": response.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )

    return response
```

## Conclusion

This implementation guide provides a foundation for developing the Financial Data API using FastAPI. By following the patterns and practices outlined here, you can create a maintainable, performant, and robust application that meets the requirements specified in the PRD.

As development progresses, continue to update this document with lessons learned and improved patterns.
