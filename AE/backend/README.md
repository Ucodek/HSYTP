# Financial Data API

A FastAPI-based backend service for financial data and portfolio analysis.

## Features

- **Authentication**: JWT-based authentication with refresh tokens
- **Financial Instruments**: CRUD operations for stocks, indices, cryptocurrencies, and ETFs
- **Internationalization**: Full i18n support with multilingual content
- **Rate Limiting**: Tier-based rate limiting (basic/premium users)
- **Caching**: Redis-based caching for optimized performance
- **Health Checks**: Comprehensive system health monitoring

## Technology Stack

- **Python 3.11+**: Modern Python with type hints
- **FastAPI**: High-performance async web framework
- **SQLAlchemy 2.0**: Async ORM for database interactions
- **PostgreSQL**: SQL database with JSON support
- **Redis**: In-memory data store for caching and rate limiting
- **Pydantic**: Data validation and settings management
- **Alembic**: Database migrations
- **Poetry**: Dependency management

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/financial-api.git
   cd financial-api
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. **Run database migrations:**
   ```bash
   poetry run alembic upgrade head
   ```

5. **Start the development server:**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

6. **Access the API documentation:**
   - OpenAPI documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/              # API endpoints
│   └── v1/           # API version 1
├── core/             # Core components (config, security)
├── crud/             # Database operations
├── db/               # Database setup and session management
├── middleware/       # Custom middleware (rate limiting)
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas for validation
├── services/         # Business logic
└── utils/            # Utility functions
```

## API Endpoints

- **Auth**: `/api/v1/auth/*` - User authentication and registration
- **Instruments**: `/api/v1/instruments/*` - Financial instruments data
- **Health**: `/health` - API health check endpoints

## Next Steps

- **Testing Implementation**: Unit and integration tests will be added in the next phase
- **Performance Optimization**: Further optimization of database queries and caching strategies
- **Market Data Integration**: Integration with external market data providers
- **Logging Enhancements**: Structured logging for better observability
- **CI/CD Setup**: Implementation of continuous integration pipeline

# Financial Data API Backend

## Development Setup

### Install dependencies
```bash
cd AE/backend
poetry install
```

### Install pre-commit hooks
```bash
cd AE/backend
poetry run pre-commit install
```

### Run tests
```bash
cd AE/backend
poetry run pytest
```

### Run linting checks manually
```bash
cd AE/backend
poetry run black .
poetry run ruff check . --fix
```

### Run the application
```bash
cd AE/backend
poetry run uvicorn app.main:app --reload
```

## Important Note
This project is part of a monorepo. All commands should be run from the `AE/backend` directory.

## Historical Data with TimescaleDB

The API uses TimescaleDB to efficiently store and query time-series financial data.

### Features
- Historical data stored in TimescaleDB hypertables for optimized performance
- Automatic time-series partitioning for efficient querying
- Support for different time intervals via time bucket aggregation

### Verification
To verify that TimescaleDB is properly set up:

```bash
poetry run python -m scripts.verify_timescaledb
```

### Test Data Generation
To insert test historical price data for demonstration purposes:

```bash
poetry run python -m scripts.insert_test_historical_data
```
