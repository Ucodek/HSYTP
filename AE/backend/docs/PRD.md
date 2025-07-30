# Financial Data API - Product Requirements Document

## Overview
This document outlines the requirements for developing a financial data API to support the frontend application. The API will provide access to stock market data, financial news, economic events, and portfolio analysis tools.

## API Specification

### Base URL
`/api/v1/`

### Authentication
- All endpoints require authentication via JWT token
- Token should be included in Authorization header: `Authorization: Bearer <token>`
- Public endpoints (if any) will be specifically marked

### Internationalization
- All API responses should support internationalization (i18n)
- Language preference is specified via `Accept-Language` header (e.g., `en-US`, `tr-TR`)
- Default language is English if not specified
- User-facing content (news, posts, event descriptions) should be available in supported languages
- Error messages and system responses should be localized
- Date and number formats should follow locale conventions

### Data Freshness Policy
- Market data (stocks, indices) will be provided with a 10-minute delay
- Each response will include a `data_timestamp` field indicating when the data was captured
- Data updates occur in batches every 10 minutes
- The API will not function as a real-time data provider
- Historical data remains unaffected by this policy

### Response Format
All API responses will follow a consistent format:

```json
{
  "success": true,
  "data": {...},
  "meta": {
    "timestamp": 1676983800,
    "data_timestamp": 1676983200,
    "pagination": {
      "total": 100,
      "limit": 10,
      "offset": 0
    }
  }
}
```

For errors:

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found"
  }
}
```

## Endpoints

### Financial Instruments

#### GET /api/v1/instruments
Returns a list of financial instruments with filtering options.

**Query Parameters:**
- `type` (string, optional): Filter by instrument type (stock, index, crypto, etf)
- `country` (string, optional): Filter by country code (USA, Turkey, etc.)
- `sort` (string, optional): Sort by field (price, change, volume)
- `order` (string, optional): Sort order (asc, desc)
- `limit` (number, optional): Number of results to return (default: 10)
- `offset` (number, optional): Offset for pagination (default: 0)

**Response:**
List of financial instruments matching the criteria.

#### GET /api/v1/instruments/:symbol
Returns detailed information about a specific financial instrument.

**Response:**
Detailed instrument information including current price, change, volume, etc.

#### GET /api/v1/instruments/:symbol/historical
Returns historical price data for a specific financial instrument.

**Query Parameters:**
- `period` (string, optional): Time period (1d, 1w, 1m, 3m, 1y, 5y)
- `interval` (string, optional): Data interval (1m, 5m, 15m, 30m, 1h, 1d)

**Response:**
Historical price data for the specified period and interval.

### Market Data

#### GET /api/v1/market/movers
Returns lists of stocks with notable price movements.

**Query Parameters:**
- `type` (string, required): Type of movers (gainers, losers, active)
- `limit` (number, optional): Number of results to return (default: 5)

**Response:**
List of stocks matching the requested mover type.

#### GET /api/v1/market/indices
Returns a list of market indices.

**Query Parameters:**
- `country` (string, optional): Filter by country
- `limit` (number, optional): Number of results to return

**Response:**
List of market indices with current values.

#### GET /api/v1/market/indices/:symbol
Returns detailed information about a specific market index.

**Response:**
Detailed index information with additional metrics (for extended indices like BIST100).

### Content

#### GET /api/v1/news
Returns financial news articles.

**Query Parameters:**
- `source` (string, optional): Filter by news source
- `limit` (number, optional): Number of articles to return
- `offset` (number, optional): Offset for pagination

**Response:**
List of news articles with timestamp, title, source, URL, and summary.

#### GET /api/v1/posts
Returns financial blog/insight posts.

**Query Parameters:**
- `category` (string, optional): Filter by category
- `limit` (number, optional): Number of posts to return
- `offset` (number, optional): Offset for pagination

**Response:**
List of blog posts with timestamp, title, URL, summary, and category.

#### GET /api/v1/events
Returns economic events and indicators.

**Query Parameters:**
- `country` (string, optional): Filter by country
- `impact` (string, optional): Filter by impact level (high, medium, low)
- `from` (timestamp, optional): Start date
- `to` (timestamp, optional): End date

**Response:**
List of economic events with details.

### Portfolio Analysis

#### POST /api/v1/portfolio/optimize
Performs portfolio optimization based on provided assets.

**Request Body:**
```json
{
  "assets": [
    {
      "symbol": "AAPL",
      "allocation": 0.25
    },
    {
      "symbol": "MSFT",
      "allocation": 0.25
    },
    ...
  ],
  "strategy": "max_sharpe"
}
```

**Response:**
Optimized portfolio allocation with expected returns, volatility, and other metrics.

#### POST /api/v1/portfolio/backtest
Performs backtesting of a portfolio against historical data.

**Request Body:**
```json
{
  "assets": [
    {
      "symbol": "AAPL",
      "allocation": 0.25
    },
    ...
  ],
  "period": "5y",
  "rebalance_frequency": "monthly"
}
```

**Response:**
Backtesting results including returns for different time periods.

#### POST /api/v1/portfolio/risk
Analyzes risk distribution in a portfolio.

**Request Body:**
```json
{
  "assets": [
    {
      "symbol": "AAPL",
      "allocation": 0.25
    },
    ...
  ]
}
```

**Response:**
Risk metrics and distribution analysis.

### Search

#### GET /api/v1/search
Performs a search across all financial instruments.

**Query Parameters:**
- `q` (string, required): Search query
- `type` (string, optional): Filter by instrument type
- `limit` (number, optional): Number of results to return

**Response:**
List of matching instruments with basic information.

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| INVALID_REQUEST | 400 | Invalid request parameters |
| UNAUTHORIZED | 401 | Authentication failed |
| FORBIDDEN | 403 | Insufficient permissions |
| RESOURCE_NOT_FOUND | 404 | Requested resource not found |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| SERVER_ERROR | 500 | Internal server error |

## Technical Requirements

### Performance
- API should respond within 200ms for simple queries
- Complex operations (like portfolio optimization) may take longer but should not exceed 5 seconds
- All endpoints should be designed to scale independently based on load

### Caching
- Implement aggressive caching for market data (10-minute TTL aligning with update frequency)
- Historical data should be heavily cached
- Different cache strategies for different data types:
  - Market data: 10-minute cache
  - News/posts: 1-hour cache
  - Historical data: 24-hour cache
  - Economic event data: 6-hour cache
- Use Redis or similar in-memory data store for frequently accessed data

### Batch Processing
- Implement scheduled batch processes for market data updates
- Run data collection and processing jobs every 10 minutes
- Optimize database operations by processing updates in batches
- Implement efficient data storage strategies that minimize writes

### Rate Limiting
- Implement rate limiting based on user tiers
- Basic tier: 100 requests per minute
- Premium tier: 500 requests per minute

### Data Sources
- Market data should be sourced from reliable financial APIs that support delayed data options
- News and events data should be aggregated from multiple sources
- Historical data should be stored in a time-series database for efficient queries
- Consider data aggregator services that already provide delayed market data at lower costs

## Implementation Phases

### Phase 1
- Basic instrument data endpoints
- Market movers and indices
- Search functionality

### Phase 2
- Historical data
- News and events
- Basic portfolio analysis

### Phase 3
- Advanced portfolio optimization
- Backtesting
- Risk analysis

## Internationalization Implementation

### Phase 1: Core Languages
- English (en-US)
- Turkish (tr-TR)

### Phase 2: Additional Languages
- German (de-DE)
- French (fr-FR)
- Spanish (es-ES)

### Implementation Strategy
- Use backend translation files for system messages and errors
- Store multilingual content in the database with language identifiers
- Implement content fallback strategy when translations aren't available
- Provide translation guidelines for content creators

## Monitoring and Analytics

- Implement logging for all API requests
- Track error rates and response times
- Monitor API usage patterns to identify optimization opportunities

---

This PRD is a living document and may be updated as requirements evolve.
