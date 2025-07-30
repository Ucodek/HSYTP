import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import get_db
from app.main import app
from app.modules.auth.models import User, UserRole

# Use a unique in-memory database for testing to avoid file I/O issues
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )

    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a FastAPI test client with a test database session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear dependency overrides after test
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user for authentication tests."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("Password123"),
        full_name="Test User",
        role=UserRole.USER,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db_session):
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("AdminPass123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def token_headers(client, test_user):
    """Get token headers for authenticated requests."""
    login_data = {
        "username": test_user.username,
        "password": "Password123",
    }
    response = client.post("/api/v1/auth/login/json", json=login_data)
    tokens = response.json()["data"]

    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
def admin_token_headers(client, test_admin):
    """Get token headers for admin authenticated requests."""
    login_data = {
        "username": test_admin.username,
        "password": "AdminPass123",
    }
    response = client.post("/api/v1/auth/login/json", json=login_data)
    tokens = response.json()["data"]

    return {"Authorization": f"Bearer {tokens['access_token']}"}


# Add new fixtures for test data generation and response validation
@pytest.fixture(scope="function")
def unique_user_data():
    """Generate unique user data for tests."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "password": "Password123",
        "full_name": f"Test User {unique_id}",
    }


@pytest.fixture(scope="function")
def inactive_user(db_session):
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        username="inactive",
        hashed_password=get_password_hash("Password123"),
        full_name="Inactive User",
        role=UserRole.USER,
        is_active=False,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def unverified_user(db_session):
    """Create an unverified test user."""
    user = User(
        email="unverified@example.com",
        username="unverified",
        hashed_password=get_password_hash("Password123"),
        full_name="Unverified User",
        role=UserRole.USER,
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
