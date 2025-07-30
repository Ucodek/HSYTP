# System Architecture

This document provides a comprehensive overview of the technical architecture of our application, including technology choices, database design, API principles, and security considerations.

## Overall System Architecture

Our application follows a modern microservices architecture with a clear separation between frontend and backend components. The system comprises:

- A single-page application (SPA) frontend
- FastAPI backend services
- PostgreSQL with TimescaleDB for persistent storage
- Redis cache for performance optimization
- Authentication service for identity management

![Deployment Architecture](https://mermaid.ink/img/pako:eNqFk81uwjAMgF_FygUk3oADmgYb2jSNw7RxQJwe3MZrRJuUJEPbxLvPCWVlMBUfSezP-WM7HUKqUkIQ3VK3yi1WrLBOUZWV2yyr7JRsYF5CiaqheVZvhVgz3liF2tSlno0A3mA1GODGdZwvi5Ep0ZMF3MN1GsHgxo9YsptZR-6D7bG7YLae3-HDTgG8LTzOfgXfSOHWkfXIw_P3HAa_DScJvA8mQd8Jr0f1Eho1za2sM926zXbjOy6qFte1uDbCMOgrLOzkY8PYg3_aN17PJI4-loqM-92IRYXrKZ_WPfGYsO14xeajSNFU9vo0m8f8jsgztB9EARVqExgZGu4XA05uScsgKKR1TMdKpZC0zJDRpanT1skF_fPMFL0zOu0OQIaq4eo_TKIlVWnhoYowCO53qJEsHJ2X_JWmZUrlB6aQBGa3YIo9dQi9Y5eQniAIa8mpVfoLXrSiMSRlKvlIfOu1tOU_BSsKGg?type=png)

## Technology Choices & Rationale

### Backend
- **Runtime Environment**: Python 3.11+ - Chosen for its strong type hinting features and excellent data science ecosystem
- **API Framework**: FastAPI - Selected for its excellent performance, built-in async support, and automatic API documentation
- **Authentication**: JWT with Auth0 - Provides secure, stateless authentication with delegated identity management

### Cache Client
- **redis-py** with async support
  - Rationale: Well-maintained official Redis client for Python

### Infrastructure
- **Self-Hosted Option**:
  - **Kubernetes** on cloud provider (AWS EKS, GCP GKE, or Azure AKS)
  - **Prometheus** + **Grafana** - Metrics and dashboards
  - **Loki** - Log aggregation

- **Managed Option**:
  - **AWS App Runner** or **Google Cloud Run** - For API service
  - **AWS RDS** or **Google Cloud SQL** - For PostgreSQL
  - **AWS ElastiCache** or **Google Memorystore** - For Redis
  - **AWS Lambda** or **Google Cloud Functions** - For scheduled data updates

### Development Tools
- **Poetry** - Dependency management
  - Rationale: Better dependency resolution and project management than pip or pipenv
  - Alternative considered: Pipenv (less powerful dependency resolution)
- **pre-commit** - Git hooks for code quality
- **mypy** - Static type checking
- **ruff** - Fast Python linter and formatter
- **Black** - Code formatting
- **isort** - Import sorting

### Testing
- **pytest** - Test framework
- **pytest-async** - For testing async code
- **pytest-cov** - For code coverage
- **hypothesis** - For property-based testing
- **Faker** - For generating test data

### CI/CD
- **GitHub Actions** - CI/CD pipeline
  - Rationale: Tight integration with GitHub and sufficient capabilities
  - Alternative considered: GitLab CI (viable if using GitLab)

### Documentation
- **MkDocs** with **Material theme** - Documentation site
- FastAPI built-in Swagger/ReDoc for API docs

### Monitoring & Observability
- **Datadog** - Primary APM and metrics platform
  - Rationale: Comprehensive monitoring with good Python integration
  - Alternative considered: New Relic (viable alternative)
- **Sentry** - Error tracking
- **structlog** - Structured logging
- **prometheus_client** - For exposing metrics

### External API Integration
- **httpx** - Modern async HTTP client
  - Rationale: Full async/await support and modern API
  - Alternative considered: aiohttp (still good but less user-friendly API)
- **tenacity** - For retries and circuit breaking

### Data Processing & Analysis
- **NumPy** and **Pandas** - For financial data manipulation
- **Scikit-learn** - For machine learning components of portfolio optimization
- **Statsmodels** - For statistical modeling
- **PyPortfolioOpt** - For portfolio optimization algorithms

## Database Design & Strategy

### Database Selection
- **Primary Database**: PostgreSQL + TimescaleDB
  - PostgreSQL: For relational data and standard queries
  - TimescaleDB extension: For time-series data (historical prices, economic events)
  - Rationale: Combines robust relational capabilities with optimized time-series storage

- **Caching Layer**: Redis
  - Used for frequently accessed data and caching
  - Perfect for storing the 10-minute delayed market data

- **Search Engine**: Elasticsearch (Optional Phase 2)
  - Advanced search capabilities for instruments and content

### Schema Design

Our database is organized around the following core entities:

#### Core Tables

**instruments**
```sql
CREATE TABLE instruments (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name JSONB NOT NULL, -- i18n support: {"en-US": "Apple Inc.", "tr-TR": "Apple Inc."}
    type VARCHAR(10) NOT NULL, -- stock, index, crypto, etf
    country VARCHAR(3),
    currency VARCHAR(3),
    description JSONB, -- i18n support
    sector VARCHAR(50),
    industry VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_instruments_type ON instruments(type);
CREATE INDEX idx_instruments_country ON instruments(country);
```

**instrument_prices (Latest Prices)**
```sql
CREATE TABLE instrument_prices (
    instrument_id INTEGER NOT NULL REFERENCES instruments(id),
    price NUMERIC(18,4) NOT NULL,
    price_change NUMERIC(18,4), -- renamed from 'change' to avoid SQL keyword
    change_percent NUMERIC(8,4),
    volume BIGINT,
    data_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (instrument_id)
);
```

**historical_data (TimescaleDB Hypertable)**
```sql
CREATE TABLE historical_data (
    instrument_id INTEGER NOT NULL REFERENCES instruments(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open NUMERIC(18,4),
    high NUMERIC(18,4),
    low NUMERIC(18,4),
    close NUMERIC(18,4) NOT NULL,
    volume BIGINT,
    adjusted_close NUMERIC(18,4), -- added field commonly used in financial APIs
    PRIMARY KEY (instrument_id, timestamp)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('historical_data', 'timestamp');
```

**market_indices**
```sql
CREATE TABLE market_indices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name JSONB NOT NULL, -- i18n support
    country VARCHAR(3),
    currency VARCHAR(3),
    description JSONB, -- i18n support
    constituents JSONB, -- Array of instrument symbols that make up the index
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**market_index_prices**
```sql
CREATE TABLE market_index_prices (
    index_id INTEGER NOT NULL REFERENCES market_indices(id),
    last_price NUMERIC(18,4) NOT NULL, -- matches mock data naming
    price_change NUMERIC(18,4), -- renamed from 'change' to avoid SQL keyword
    change_percent NUMERIC(8,4),
    volume BIGINT,
    previous_close NUMERIC(18,4),
    period_high NUMERIC(18,4), -- renamed from day_high_price for consistency
    period_low NUMERIC(18,4), -- renamed from day_low_price for consistency
    w52_high NUMERIC(18,4), -- renamed from 52_w_high_price for SQL compatibility
    w52_low NUMERIC(18,4), -- renamed from 52_w_low_price for SQL compatibility
    data_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (index_id)
);
```

**news**
```sql
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    title JSONB NOT NULL, -- i18n support
    source VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    summary JSONB, -- i18n support
    cover VARCHAR(255), -- image URL as in mock data
    external_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_news_timestamp ON news(timestamp);
```

**posts**
```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    title JSONB NOT NULL, -- i18n support
    summary JSONB NOT NULL, -- i18n support
    content JSONB, -- i18n support
    category VARCHAR(50) NOT NULL,
    url VARCHAR(255) NOT NULL,
    author_name VARCHAR(100), -- Name of the content creator/admin (not user-generated)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_posts_category ON posts(category);
CREATE INDEX idx_posts_timestamp ON posts(timestamp);
```

**economic_events**
```sql
CREATE TABLE economic_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    event JSONB NOT NULL, -- i18n support
    country VARCHAR(3) NOT NULL,
    impact VARCHAR(10) NOT NULL, -- high, medium, low
    previous_value NUMERIC(18,4),
    forecast_value NUMERIC(18,4),
    actual_value NUMERIC(18,4),
    unit VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_economic_events_timestamp ON economic_events(timestamp);
CREATE INDEX idx_economic_events_country ON economic_events(country);
```

**users**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    subscription_tier VARCHAR(20) DEFAULT 'basic', -- basic or premium
    language_preference VARCHAR(10) DEFAULT 'en-US', -- user's preferred language
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
```

**Portfolio Analysis Tables**

```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL, -- Reference to users table
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE portfolio_assets (
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    instrument_id INTEGER NOT NULL REFERENCES instruments(id),
    allocation NUMERIC(5,4) NOT NULL, -- Percentage as decimal (0.25 = 25%)
    PRIMARY KEY (portfolio_id, instrument_id)
);

CREATE TABLE portfolio_optimizations (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id),
    strategy VARCHAR(50) NOT NULL,
    expected_return NUMERIC(6,4),
    volatility NUMERIC(6,4),
    sharpe_ratio NUMERIC(6,4),
    sortino_ratio NUMERIC(6,4),
    optimization_results JSONB NOT NULL, -- Stores detailed results including asset weights
    risk_distribution JSONB, -- Based on mock data structure
    backtesting_results JSONB, -- To store 1y, 3y, 5y returns as in mock data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Authentication Tables**

```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

CREATE TABLE rate_limits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(100) NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (user_id, endpoint, window_start)
);

CREATE INDEX idx_rate_limits_window ON rate_limits(user_id, endpoint, window_start);
```

### Data Management Strategy

#### Store Locally
- **Instrument Metadata**: Basic reference data about all instruments
- **Latest Price Snapshots**: The 10-minute delayed data
- **Recent Historical Data**: 1-3 months of historical prices
- **Content Data**: News summaries, posts (created by administrators/content team), economic event calendar
- **User Data**: Portfolios, optimization results, user preferences

#### Source from External APIs
- **Extended Historical Data**: Historical data beyond 3 months
- **Detailed Company Information**: Company financials, earnings data
- **Advanced Market Metrics**: Complex indicators, sentiment analysis
- **Full News Articles**: Link to original sources for complete content

### Data Synchronization Strategy

#### Market Data Update Process
```
1. Scheduler triggers update job every 10 minutes
2. External API clients fetch latest data for tracked instruments
3. Batch processor prepares data for database insertion
4. Database transaction updates instrument_prices table
5. Cache invalidation signals are sent to Redis
6. Redis caches are updated with new data
7. Metrics on update process are logged
```

#### Historical Data Collection
```
1. Daily job collects previous day's historical data
2. Time-series data is inserted into historical_data table
3. Older data is summarized and compressed over time
4. Rarely accessed historical data is archived
```

### Data Retention Policy

| Data Type | Active Storage | Archive | Purge |
|-----------|---------------|---------|-------|
| Price Snapshots | 30 days | 1 year | > 1 year |
| Historical (minute) | 30 days | 1 year | > 1 year |
| Historical (hourly) | 90 days | 5 years | > 5 years |
| Historical (daily) | 5 years | 20 years | Never |
| News | 30 days | 1 year | > 1 year |
| Economic Events | 1 year | 5 years | > 5 years |
| Portfolio Analysis | 1 year | Never | Never |

### Optimization Strategies

1. **Partitioning**
   - **Time-based partitioning** for historical data tables
   ```sql
   -- Monthly partitioning example for TimescaleDB
   SELECT create_hypertable('historical_data', 'timestamp',
     chunk_time_interval => interval '1 month');
   ```

2. **Indexing Strategy**
   - **Compound indices** for common query patterns
   ```sql
   -- Example for efficient historical data queries
   CREATE INDEX idx_hist_instrument_time ON historical_data(instrument_id, timestamp DESC);
   ```
   - **Partial indices** for frequently filtered subsets
   ```sql
   -- Example for top US stocks
   CREATE INDEX idx_us_stocks ON instruments(symbol)
   WHERE country = 'USA' AND type = 'stock';
   ```

3. **Caching Hierarchy**
   - **Application Memory**: Ultra-fast access for reference data
   - **Redis Layer 1**: 10-minute market data cache (high throughput)
   - **Redis Layer 2**: Aggregated data, search results (medium throughput)
   - **Database Query Cache**: For complex queries (lower throughput)

## API Design Principles

### API Architecture
- **Style**: RESTful API - Chosen for simplicity, scalability, and broad framework/client support
- **Framework**: FastAPI - Selected for its excellent performance, built-in async support, and automatic API documentation

### Endpoint Structure
- Resources are named using plural nouns (users, instruments, portfolios)
- Nested resources use hierarchical paths (/portfolios/{id}/assets)
- Operations follow standard HTTP methods:
  - GET for retrieval
  - POST for creation
  - PUT for full updates
  - PATCH for partial updates
  - DELETE for removal

### Error Handling
- HTTP status codes used appropriately (200, 201, 400, 401, 403, 404, 500)
- Consistent error response format:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found",
    "details": {}
  }
}
```

## Security Architecture

### Authentication
- **Method**: JWT (JSON Web Tokens) - Provides stateless authentication with secure, signed tokens
- **Session Management**: Token-based with refresh tokens - Access tokens expire after 15 minutes, refresh tokens enable seamless re-authentication

### Authorization
- **Access Control Model**: Role-Based Access Control (RBAC)
- **Role-Based Permissions**: Different access levels based on subscription tier (basic vs premium)

### Data Protection
- **Encryption Strategy**:
  - Data in transit: TLS 1.3
  - Sensitive data at rest: AES-256 encryption
  - Password storage: bcrypt with appropriate work factor

## Data Flow

1. **Real-time Market Data**:
   ```
   External API → Celery Worker → PostgreSQL/Redis → API Endpoints → Client
   ```

2. **Portfolio Analysis**:
   ```
   Client Request → API → Portfolio Service → Optimization Engine (NumPy/SciKit) → Response
   ```

3. **Search Functionality**:
   ```
   Query → API → PostgreSQL Full-Text Search (Phase 1) or Elasticsearch (Phase 2) → Results
   ```

## Search Implementation Strategy

### Phase 1: PostgreSQL Full-Text Search

For the initial implementation, we'll leverage PostgreSQL's built-in full-text search capabilities:

```sql
-- Add search vectors to instruments table
ALTER TABLE instruments ADD COLUMN search_vector tsvector;

-- Generate search vectors from multiple fields
CREATE FUNCTION update_instrument_search_vector() RETURNS trigger AS $$
BEGIN
  NEW.search_vector =
    setweight(to_tsvector('english', COALESCE(NEW.symbol, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.name->>'en-US', '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(NEW.sector, '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(NEW.industry, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- Create trigger to update search vector on insert or update
CREATE TRIGGER instrument_search_update
BEFORE INSERT OR UPDATE ON instruments
FOR EACH ROW EXECUTE FUNCTION update_instrument_search_vector();

-- Create GIN index for fast search
CREATE INDEX idx_instruments_search ON instruments USING GIN (search_vector);
```

### Phase 2: Elasticsearch Integration

When the platform scales and requires more advanced search capabilities:

1. **Data Synchronization**: Implement a sync process that keeps Elasticsearch updated with changes from PostgreSQL
2. **Query Optimization**: Configure custom analyzers for financial terms and instrument symbols
3. **Advanced Features**: Implement fuzzy matching, synonyms, and typo tolerance

## Internationalization Implementation

### Data Storage Approach

1. **JSONB for Multilingual Text**
   ```json
   {
     "en-US": "Understanding Market Volatility",
     "tr-TR": "Piyasa Volatilitesini Anlamak",
     "de-DE": "Marktvolatilität verstehen"
   }
   ```

2. **Querying Multilingual Fields**
   ```sql
   -- Example query for retrieving appropriate language
   SELECT id, symbol, name->>:language AS translated_name
   FROM instruments
   WHERE name ? :language
   ORDER BY name->>:language;
   ```

3. **Default Language Fallback**
   ```sql
   -- Fallback logic in query
   SELECT
     id,
     COALESCE(
       name->>:language,
       name->>'en-US'
     ) AS translated_name
   FROM instruments;
   ```

## Backup and Disaster Recovery

1. **Regular Backups**
   - Full database backup: Daily
   - Transaction logs: Every 10 minutes
   - Configuration backups: Weekly

2. **Recovery Strategy**
   - Point-in-time recovery capability
   - Multi-region replication for critical data
   - Read replicas that can be promoted to master

## Monitoring and Analytics

### Third-Party Logging and Monitoring

1. **Application Performance Monitoring (APM)**:
   - Use services like Datadog, New Relic, or Elastic APM
   - Instrument FastAPI application with APM agent
   - Track endpoint performance, errors, and resource utilization

2. **Error Logging**:
   - Integrate with Sentry for real-time error tracking
   - Configure structured logging with proper context
   - Implement correlation IDs across services

3. **Usage Analytics**:
   - Implement API usage tracking through middleware
   - Store aggregated metrics in time-series format
   - Create dashboards for visualizing API usage patterns

### Logging Implementation

```python
# Example FastAPI middleware for request logging with third-party service
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate correlation ID for request tracing
    correlation_id = str(uuid.uuid4())

    # Add context to logs
    with logger.contextualize(
        correlation_id=correlation_id,
        endpoint=request.url.path,
        method=request.method
    ):
        try:
            # Process the request and measure response time
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log successful request with timing info
            logger.info(
                "Request processed",
                status_code=response.status_code,
                duration=process_time
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            return response

        except Exception as e:
            # Capture exception with third-party error tracking
            sentry_sdk.capture_exception(e)
            logger.exception("Request failed")
            raise
```

## Package Dependencies

Below is a sample `pyproject.toml` file showing core dependencies:

```toml
[tool.poetry]
name = "financial-api"
version = "0.1.0"
description = "Financial Data API"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.23.2"}
gunicorn = "^21.2.0"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.22"}
alembic = "^1.12.0"
asyncpg = "^0.28.0"
psycopg2-binary = "^2.9.9"
redis = {extras = ["hiredis"], version = "^5.0.1"}
celery = "^5.3.4"
httpx = "^0.25.0"
pydantic = {extras = ["email"], version = "^2.4.2"}
pydantic-settings = "^2.0.3"
tenacity = "^8.2.3"
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
python-multipart = "^0.0.6"
numpy = "^1.26.1"
pandas = "^2.1.1"
scikit-learn = "^1.3.1"
statsmodels = "^0.14.0"
pyportfolioopt = "^1.5.5"
structlog = "^23.2.0"
ddtrace = "^1.19.0"
babel = "^2.13.0"
apscheduler = "^3.10.4"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.2"
pytest-cov = "^4.1.0"
pytest-asyncio = "^0.21.1"
mypy = "^1.6.1"
ruff = "^0.1.0"
black = "^23.10.0"
isort = "^5.12.0"
ipython = "^8.16.1"
pre-commit = "^3.5.0"
hypothesis = "^6.87.1"
faker = "^19.10.0"
mkdocs = "^1.5.3"
mkdocs-material = "^9.4.5"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Data Sources

### Market Data Providers
- **Alpha Vantage**: Good for delayed stock data
- **Yahoo Finance API**: Comprehensive but with usage limitations
- **Financial Modeling Prep**: Good balance of features/price

### News and Events
- **NewsAPI**: Aggregated financial news
- **Trading Economics**: Economic events and indicators

### Historical Data
- **Alpha Vantage**: Historical EOD data
- **Yahoo Finance**: Historical OHLCV data
- **IEX Cloud**: US market data (premium option)

## System Constraints & Limitations

### Performance Benchmarks

| Query Type | Target Response Time | Max Load |
|------------|---------------------|----------|
| Instrument lookup | < 50ms | 1000 qps |
| Price snapshot | < 100ms | 500 qps |
| Historical data (1d) | < 200ms | 200 qps |
| Historical data (1y) | < 500ms | 50 qps |
| Portfolio optimization | < 3s | 10 qps |

### Version Requirements & Compatibility

| Component | Version | Notes |
|-----------|---------|-------|
| Python | ≥ 3.11 | Type hinting features needed |
| FastAPI | ≥ 0.104.0 | For latest features and fixes |
| PostgreSQL | ≥ 14.0 | For best JSONB performance |
| Redis | ≥ 7.0 | For improved memory management |
| SQLAlchemy | ≥ 2.0 | For improved async support |
| Pydantic | ≥ 2.0 | For best validation performance |

### Scaling Considerations

- **Horizontal Scaling**: API and workers designed for horizontal scaling
- **Database Scaling**:
  - Read replicas for read-heavy operations
  - Connection pooling with PgBouncer
  - TimescaleDB partitioning for large time-series datasets
- **Cache Strategy**:
  - Multi-level caching (application, Redis, database)
  - Cache invalidation patterns designed for concurrent access
