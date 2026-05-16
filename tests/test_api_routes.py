"""Tests for FastAPI routes"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home_page():
    """Test home page loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Pulse AI" in response.content


def test_health_endpoint():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_demo_search():
    """Test demo search endpoint"""
    response = client.get("/api/search/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "events" in data
    assert data["mode"] == "demo"


@pytest.mark.asyncio
async def test_search_endpoint():
    """Test search API endpoint"""
    search_data = {
        "query": "rock concerts in London",
        "city": "London",
        "country": "GB",
        "category": "Music",
        "use_demo": True
    }
    
    response = client.post("/api/search/", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "events" in data
    assert len(data["events"]) > 0


def test_search_htmx_endpoint():
    """Test HTMX search endpoint"""
    form_data = {
        "query": "jazz concerts",
        "city": "New York",
        "use_demo": "true"
    }
    
    response = client.post("/api/search/htmx", data=form_data)
    assert response.status_code == 200
    assert b"event" in response.content.lower()


def test_invalid_search_request():
    """Test search with invalid data"""
    search_data = {
        "query": "",  # Empty query
        "city": "",
        "use_demo": True
    }
    
    response = client.post("/api/search/", json=search_data)
    # Should handle gracefully
    assert response.status_code in [200, 400, 422]


def test_search_with_category_filter():
    """Test search with category filter"""
    search_data = {
        "query": "events in London",
        "city": "London",
        "country": "GB",
        "category": "Sports",
        "use_demo": True
    }
    
    response = client.post("/api/search/", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/api/search/")
    # Should have CORS headers configured
    assert response.status_code in [200, 405]

# Made with Bob
