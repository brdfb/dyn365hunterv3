"""Shared pytest fixtures and utilities for test isolation and setup.

This module provides standardized test fixtures that ensure:
- Transaction-based test isolation (automatic rollback)
- Consistent database session management
- Proper cleanup after each test
- Redis/Celery availability checks for integration tests
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.db.models import Base

# Test database URL - Priority: TEST_DATABASE_URL > HUNTER_DATABASE_URL > DATABASE_URL > default
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "HUNTER_DATABASE_URL",
        os.getenv(
            "DATABASE_URL",
            "postgresql://dyn365hunter:password123@localhost:5432/dyn365hunter",
        ),
    ),
)

# Test Redis URL
TEST_REDIS_URL = os.getenv(
    "TEST_REDIS_URL",
    os.getenv(
        "HUNTER_REDIS_URL",
        os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    ),
)


@pytest.fixture(scope="function")
def db_session():
    """Create an isolated test database session with transaction rollback.
    
    This fixture provides:
    - Transaction-based isolation (each test runs in its own transaction)
    - Automatic rollback after test completion
    - Proper cleanup of connections and engine
    
    Usage:
        def test_something(db_session):
            # Test code here
            # All changes will be rolled back automatically
    """
    engine = create_engine(TEST_DATABASE_URL)

    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
    except OperationalError as e:
        pytest.skip(f"Test database not available: {TEST_DATABASE_URL} - {e}")

    # Create tables (if not exist)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Start a transaction for test isolation
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        # Rollback transaction to ensure test isolation
        transaction.rollback()
        session.close()
        connection.close()
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with isolated database session.
    
    This fixture:
    - Overrides the database dependency with the test session
    - Provides a FastAPI TestClient
    - Cleans up dependency overrides after test
    
    Usage:
        def test_endpoint(client):
            response = client.get("/endpoint")
            assert response.status_code == 200
    """
    # Import app here to avoid import-time database connection
    from app.main import app
    from app.db.session import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def is_redis_available():
    """Check if Redis is available for testing.
    
    Returns:
        bool: True if Redis is available, False otherwise
    """
    try:
        import redis
        r = redis.from_url(TEST_REDIS_URL)
        r.ping()
        return True
    except Exception:
        return False


def is_celery_available():
    """Check if Celery worker is available for testing.
    
    Returns:
        bool: True if Celery is configured and available, False otherwise
    """
    try:
        from app.core.tasks import celery_app
        # Check if Celery broker is configured
        return celery_app.conf.broker_url is not None
    except Exception:
        return False


@pytest.fixture(scope="function")
def redis_available():
    """Fixture that skips test if Redis is not available.
    
    Usage:
        def test_redis_feature(redis_available):
            # Test code that requires Redis
    """
    if not is_redis_available():
        pytest.skip("Redis not available for testing")
    return True


@pytest.fixture(scope="function")
def celery_available():
    """Fixture that skips test if Celery is not available.
    
    Usage:
        def test_celery_task(celery_available):
            # Test code that requires Celery
    """
    if not is_celery_available():
        pytest.skip("Celery not available for testing")
    return True


@pytest.fixture(scope="function")
def redis_and_celery_available():
    """Fixture that skips test if both Redis and Celery are not available.
    
    Usage:
        def test_integration(redis_and_celery_available):
            # Test code that requires both Redis and Celery
    """
    if not is_redis_available():
        pytest.skip("Redis not available for testing")
    if not is_celery_available():
        pytest.skip("Celery not available for testing")
    return True


def pytest_configure(config):
    """Pytest configuration hook.
    
    Adds custom markers for conditional test execution.
    """
    config.addinivalue_line(
        "markers", "requires_redis: mark test as requiring Redis"
    )
    config.addinivalue_line(
        "markers", "requires_celery: mark test as requiring Celery"
    )
    config.addinivalue_line(
        "markers", "requires_integration: mark test as requiring Redis and Celery"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically skip tests marked with requires_* if dependencies are not available."""
    for item in items:
        # Check for requires_redis marker
        if item.get_closest_marker("requires_redis"):
            if not is_redis_available():
                skip_marker = pytest.mark.skip(reason="Redis not available")
                item.add_marker(skip_marker)
        
        # Check for requires_celery marker
        if item.get_closest_marker("requires_celery"):
            if not is_celery_available():
                skip_marker = pytest.mark.skip(reason="Celery not available")
                item.add_marker(skip_marker)
        
        # Check for requires_integration marker
        if item.get_closest_marker("requires_integration"):
            if not is_redis_available() or not is_celery_available():
                skip_marker = pytest.mark.skip(
                    reason="Redis and/or Celery not available"
                )
                item.add_marker(skip_marker)

