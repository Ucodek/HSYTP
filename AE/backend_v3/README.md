# HSYTP API (backend_v3)

A high-performance, modular FastAPI backend for financial data, analytics, and AI-driven services. This project provides secure, scalable RESTful APIs for user authentication, financial instrument management, and more, designed for integration with modern financial applications.

## Features

- **User Authentication:** Register, login, JWT-based authentication, token refresh, password management.
- **Financial Instruments:** CRUD operations, price history, filtering, and analytics for financial instruments.
- **Modular Architecture:** Extensible modules for authentication, instruments, and more.
- **Scheduler Integration:** Background job scheduling with APScheduler.
- **Database Support:** Async PostgreSQL (via SQLAlchemy/asyncpg), Alembic migrations.
- **Caching & Rate Limiting:** Redis-based caching and request rate limiting.
- **Monitoring:** Health and metrics endpoints for observability.
- **Production Ready:** Uvicorn/Gunicorn support, environment-based configuration.

## Quick Start

### 1. Clone the Repository
```sh
git clone https://github.com/smart-tech-arge/HSYTP.git
cd AE/backend_v3
```

### 2. Install Dependencies
This project uses [Poetry](https://python-poetry.org/) for dependency management.
```sh
poetry install
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in the required values:
```sh
cp .env.example .env
```
- Set your database, cache, and JWT secrets as needed.

### 4. Initialize Database and Alembic
Copy the Alembic example config and initialize the database:
```sh
cp alembic.ini.example alembic.ini
```
If you are using a fresh (empty) database, simply run the migration command below. Alembic will create all tables as defined in the existing migration scripts:
```sh
poetry run alembic upgrade head
```

> **Note:** Only run `poetry run alembic revision --autogenerate -m "Your message"` if you have made changes to the models and want to create a new migration file.

### 5. Start the Development Server
```sh
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation
- Swagger UI: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- ReDoc: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

## Project Structure
```
backend_v3/
├── app/
│   ├── main.py           # FastAPI app entry point
│   ├── api/              # API routers
│   ├── modules/          # Modular business logic (auth, instruments, ...)
│   ├── scheduler/        # Background job scheduler
│   └── ...
├── migrations/           # Alembic migrations
├── pyproject.toml        # Poetry project config
├── .env.example          # Example environment variables
└── ...
```

## Environment Variables
See `.env.example` for all configuration options, including:
- `APP_NAME`, `VERSION`, `DEBUG`
- `DATABASE_URL` (PostgreSQL connection string)
- `CACHE_URL` (Redis connection string)
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`, etc.
- CORS, rate limiting, monitoring paths

## Development & Contribution
- Code style: [Black](https://black.readthedocs.io/), [isort](https://pycqa.github.io/isort/), [Ruff](https://docs.astral.sh/ruff/)
- Run tests and linters before submitting PRs.
- Contributions are welcome! Please open issues or pull requests.

## License
[MIT](LICENSE)  

## Authors
- Abdulkadir Eyigül (<mr.eyigul@gmail.com>)

---
For more details, see the API docs or explore the codebase.
