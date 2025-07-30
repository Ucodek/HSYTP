import asyncio
import sys
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.crud.users import user as user_crud
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.users import User
from app.schemas.users import UserCreate

# Fix for Windows: Set event loop policy to use SelectSelector instead of Proactor
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Determine which database to use for testing
if settings.SQLALCHEMY_DATABASE_URI:
    # Use the same database URI that the app is configured to use
    # This ensures we use the same driver (psycopg vs psycopg2)
    TEST_SQLALCHEMY_DATABASE_URI = str(settings.SQLALCHEMY_DATABASE_URI)
else:
    # Use a dedicated PostgreSQL test database for local development
    TEST_SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/test_financial_data"

print(f"Using test database: {TEST_SQLALCHEMY_DATABASE_URI}")

# Create async engine for tests
test_engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URI, poolclass=NullPool)
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# Override the dependency with our test database
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    # Use the WindowsSelectorEventLoopPolicy for Windows
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database() -> None:
    """Set up the test database."""
    # If we're using the main database for tests
    if settings.DATABASE_URL and TEST_SQLALCHEMY_DATABASE_URI == settings.DATABASE_URL:
        # Be very careful about not dropping tables -
        # we don't want to affect production data
        # Instead, we'll just clean specific test data at the end
        print(
            "WARNING: Using main database for testing! Will only clean test-specific records."
        )
        yield
        # Only clean up test-specific records here (not implemented for brevity)
        return

    # For local development with a dedicated test database, we can recreate all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.drop_all
        )  # First drop all tables if they exist
        await conn.run_sync(Base.metadata.create_all)  # Then create fresh tables
    yield
    # Drop all tables after tests are done
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(setup_database) -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
async def test_user(setup_database) -> User:
    """Create a test user for authentication tests"""
    TEST_USER_EMAIL = "test@example.com"
    TEST_USER_PASSWORD = "TestPassword123"  # Follows password validation rules

    async with TestingSessionLocal() as db:
        # Check if test user already exists
        user = await user_crud.get_by_email(db, email=TEST_USER_EMAIL)
        if not user:
            # Create test user
            user_in = UserCreate(
                email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, is_active=True
            )
            user = await user_crud.create(db, obj_in=user_in)
        return user


@pytest.fixture
async def auth_headers(test_user: User, client: TestClient) -> dict:
    """Get authorization headers for authenticated requests"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "test@example.com", "password": "TestPassword123"},
    )
    tokens = response.json()

    # Update to handle the new response structure where tokens are in the "data" field
    access_token = tokens.get("data", {}).get("access_token") or tokens.get(
        "access_token"
    )

    return {"Authorization": f"Bearer {access_token}"}
