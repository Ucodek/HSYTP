# Financial Data Platform - Backend Project Structure

This document outlines the recommended project structure for the FastAPI backend implementation of the Financial Data Platform.

## Directory Structure

```
financial-api/
├── app/                        # Main application directory
│   ├── api/                    # API routes
│   │   ├── v1/                 # API version 1
│   │   │   ├── endpoints/      # API endpoint modules
│   │   │   │   ├── instruments.py
│   │   │   │   ├── market.py
│   │   │   │   ├── news.py
│   │   │   │   ├── posts.py
│   │   │   │   ├── events.py
│   │   │   │   ├── portfolio.py
│   │   │   │   └── search.py
│   │   │   ├── dependencies.py # Shared dependencies
│   │   │   └── router.py      # Main router that includes all endpoints
│   │   └── deps/              # Shared dependencies across API versions
│   ├── core/                   # Core application components
│   │   ├── config.py          # Configuration settings
│   │   ├── security.py        # Authentication and security
│   │   └── errors.py          # Error handling
│   ├── db/                     # Database related code
│   │   ├── base.py            # Base DB setup
│   │   ├── session.py         # DB session management
│   │   └── init_db.py         # Database initialization
│   ├── models/                 # SQLAlchemy models (database schema)
│   │   ├── instruments.py
│   │   ├── market.py
│   │   ├── news.py
│   │   ├── posts.py
│   │   ├── events.py
│   │   ├── portfolio.py
│   │   └── users.py
│   ├── schemas/                # Pydantic models (data validation)
│   │   ├── instruments.py
│   │   ├── market.py
│   │   ├── news.py
│   │   ├── posts.py
│   │   ├── events.py
│   │   ├── portfolio.py
│   │   └── users.py
│   ├── crud/                   # CRUD operations
│   │   ├── base.py            # Base CRUD class with generic methods
│   │   ├── instruments.py
│   │   ├── market.py
│   │   ├── news.py
│   │   ├── posts.py
│   │   ├── events.py
│   │   ├── portfolio.py
│   │   └── users.py
│   ├── services/               # Business logic layer
│   │   ├── instruments_service.py
│   │   ├── market_service.py
│   │   ├── news_service.py
│   │   ├── posts_service.py
│   │   ├── events_service.py
│   │   ├── portfolio_service.py
│   │   ├── optimization_service.py  # Portfolio optimization algorithms
│   │   └── search_service.py
│   ├── clients/                # External API clients
│   │   ├── base_client.py     # Base API client class
│   │   ├── alpha_vantage.py   # Alpha Vantage API client
│   │   ├── yahoo_finance.py   # Yahoo Finance API client
│   │   └── news_api.py        # News API client
│   ├── tasks/                  # Background tasks
│   │   ├── worker.py          # Celery worker configuration
│   │   ├── market_data.py     # Market data update tasks
│   │   └── historical_data.py # Historical data collection tasks
│   ├── utils/                  # Utility functions
│   │   ├── i18n.py            # Internationalization utilities
│   │   ├── time_utils.py      # Time/date utilities
│   │   └── validators.py      # Custom validators
│   ├── middleware/             # Custom middleware
│   │   ├── logging.py         # Logging middleware
│   │   └── rate_limiting.py   # Rate limiting middleware
│   ├── cache/                  # Caching strategies
│   │   ├── redis_cache.py     # Redis cache implementation
│   │   └── cache_keys.py      # Cache key generation
│   ├── localization/           # Internationalization resources
│   │   ├── en-US/             # English translations
│   │   └── tr-TR/             # Turkish translations
│   ├── logging/                # Logging configuration
│   │   └── config.py          # Logging setup
│   └── ml/                     # Machine learning models (for portfolio optimization)
│       ├── models/            # Model implementations
│       ├── data/              # Data preparation for models
│       └── optimization/      # Optimization algorithms
├── migrations/                 # Alembic migrations
│   ├── versions/              # Migration versions
│   ├── env.py                 # Migration environment
│   └── alembic.ini            # Alembic configuration
├── tests/                      # Test directory
│   ├── api/                   # API tests
│   ├── services/              # Service tests
│   ├── models/                # Model tests
│   └── conftest.py            # Test configuration/fixtures
├── scripts/                    # Utility scripts
│   ├── seed_db.py            # Seed database with initial data
│   └── generate_keys.py      # Generate security keys
├── alembic.ini                 # Alembic configuration file
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment variables
├── pyproject.toml              # Project dependencies (Poetry)
├── poetry.lock                 # Locked dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose configuration
└── main.py                     # Application entry point
```

## Component Architecture

### Layer Organization

The application follows a layered architecture:

1. **API Layer** (`app/api/`)
   - Handles HTTP requests and responses
   - Input validation
   - Authentication and authorization
   - Routing to appropriate services

2. **Service Layer** (`app/services/`)
   - Contains business logic
   - Orchestrates operations across multiple repositories
   - Implements domain-specific rules

3. **Data Access Layer** (`app/crud/`)
   - Provides database operations
   - Abstracts database implementation details
   - Handles data persistence and retrieval

4. **External Services Layer** (`app/clients/`)
   - Manages communication with external APIs
   - Handles retry logic, rate limiting, and error handling
   - Transforms external data to internal formats

### Dependency Flow

```
API Endpoints → Services → CRUD/Repositories → Database
     ↑              ↑             ↑
     |              |             |
    Auth         External       Cache
 Middleware       Clients      Strategy
```

## Key Design Patterns

### 1. Repository Pattern (via CRUD modules)

Centralizes data access operations and provides a clean abstraction over database operations.

```python
# Example from app/crud/base.py
class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    # More generic CRUD operations...
```

### 2. Dependency Injection

FastAPI's dependency injection system is used extensively to provide services and repositories to endpoints.

```python
# Example from app/api/v1/endpoints/instruments.py
@router.get("/{symbol}")
async def get_instrument(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    instruments_service: InstrumentsService = Depends(get_instruments_service)
):
    # Implementation using injected dependencies
```

### 3. Data Transfer Objects (DTOs)

Pydantic models are used for data validation and serialization.

```python
# Example from app/schemas/instruments.py
class InstrumentBase(BaseModel):
    symbol: str
    name: str
    type: InstrumentType

class InstrumentCreate(InstrumentBase):
    # Additional fields for creation

class InstrumentResponse(InstrumentBase):
    id: int
    price: Optional[float] = None
    change: Optional[float] = None

    class Config:
        orm_mode = True
```

## Configuration Management

### Environment Variables

Application configuration is managed through environment variables loaded via python-dotenv:

```python
# Example from app/core/config.py
class Settings(BaseSettings):
    PROJECT_NAME: str = "Financial Data API"
    API_V1_STR: str = "/api/v1"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    # More configuration settings...

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### Feature Flags

Feature flags are used to enable/disable specific functionality:

```python
# In settings
ENABLE_ELASTICSEARCH: bool = False
USE_REDIS_CACHE: bool = True
```

## Authentication Flow

```
Client → JWT Auth Middleware → Protected Endpoint
   ↑            |
   |            v
   └─────── Token Verification
```

## Internationalization Strategy

1. **Request Flow**:
   - Client sends `Accept-Language` header
   - Middleware extracts language preference
   - Services fetch appropriate language content

2. **Content Access**:
   - Database JSONB fields for multilingual content
   - Utility functions to extract content in requested language
   - Fallback to default language when translation missing

## Background Task Processing

```
Scheduler → Task Queue (Celery) → Workers
                   ↓
        Database Updates → Cache Invalidation
```

## Testing Strategy

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test HTTP endpoints
4. **Performance Tests**: Ensure system meets performance targets

## Development Workflow

1. **Local Development**:
   - Run PostgreSQL, Redis, and other dependencies via Docker Compose
   - Run API with auto-reload for development

2. **Testing**:
   - Run tests with pytest
   - Use test database for isolation

3. **Deployment**:
   - Build Docker image
   - Deploy to container orchestration platform (e.g., Kubernetes)

---

This document provides a blueprint for organizing the FastAPI backend implementation. It should be used as a guide when developing the financial data platform.
