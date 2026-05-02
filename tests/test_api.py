"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    """Test that the health check endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_loads(client):
    """Test that the dashboard HTML loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"AI Signal Control Room" in response.content


def test_run_without_api_key(client):
    """Test that /run requires API key."""
    response = client.post("/run")
    assert response.status_code == 401
    assert "Missing API key" in response.json()["detail"]


def test_run_with_invalid_api_key(client):
    """Test that invalid API key is rejected."""
    headers = {"X-API-Key": "invalid-key"}
    response = client.post("/run", headers=headers)
    assert response.status_code == 403
    assert "Invalid API key" in response.json()["detail"]


def test_run_with_valid_api_key(client, valid_headers):
    """Test that /run works with valid API key."""
    response = client.post("/run", headers=valid_headers)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "message" in data


def test_status_endpoint(client, valid_headers):
    """Test that /status endpoint requires valid job ID."""
    response = client.get("/status/invalid-job-id", headers=valid_headers)
    assert response.status_code == 404


def test_metrics_endpoint(client):
    """Test that /metrics returns data (or handles missing data gracefully)."""
    response = client.get("/metrics")
    # May return 404 if no metrics yet, that's OK
    assert response.status_code in [200, 404]


def test_deployment_endpoint(client):
    """Test that /deployment returns data or 404."""
    response = client.get("/deployment")
    assert response.status_code in [200, 404]


def test_rag_status_endpoint(client):
    """Test that /rag/status returns collection status."""
    response = client.get("/rag/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

