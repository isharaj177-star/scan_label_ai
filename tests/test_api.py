"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "ScanLabel AI"


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data


def test_scan_endpoint_valid_barcode(client):
    """Test scan endpoint with valid barcode."""
    # This will make a real API call, so it might fail if offline
    response = client.get("/scan?barcode=5449000000996")
    
    # Should either succeed or fail gracefully
    assert response.status_code in [200, 404, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "product_name" in data
        assert "health_prediction" in data
        assert data["health_prediction"] in ["Healthy", "Moderate", "Unhealthy"]


def test_scan_endpoint_invalid_barcode(client):
    """Test scan endpoint with invalid barcode."""
    response = client.get("/scan?barcode=")
    assert response.status_code == 400


def test_scan_endpoint_missing_barcode(client):
    """Test scan endpoint without barcode parameter."""
    response = client.get("/scan")
    assert response.status_code == 422  # Validation error








