"""Test configuration and fixtures."""

import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def api_key():
    """Return the default API key for testing."""
    return "dev-key-change-in-production"


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    from apps.api.app import app

    return TestClient(app)


@pytest.fixture
def valid_headers(api_key):
    """Return headers with valid API key."""
    return {"X-API-Key": api_key}
