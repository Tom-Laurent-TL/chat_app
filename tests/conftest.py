"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.shared.database.service import init_db, reset_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize database tables before running tests."""
    init_db()
    yield
    # Reset database after all tests (optional)
    # reset_db()


@pytest.fixture(autouse=True)
def reset_db_after_test():
    """Reset database after each test to ensure test isolation."""
    yield
    reset_db()  # Reset database after each test


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)
