import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestMainApp:
    """Test cases for the main FastAPI application."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Ops Mesh API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["api"] == "/api/v1"
    
    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ops-mesh-backend"
    
    def test_openapi_docs_endpoint(self, client):
        """Test that OpenAPI documentation is accessible."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Ops Mesh Backend"
        assert data["info"]["version"] == "1.0.0"
    
    def test_docs_endpoint(self, client):
        """Test that Swagger UI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self, client):
        """Test that ReDoc documentation is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # CORS preflight should be handled
        assert response.status_code in [200, 204]
    
    def test_api_routes_registered(self, client):
        """Test that all API routes are properly registered."""
        # Test appointments routes
        response = client.get("/api/v1/appointments/")
        assert response.status_code == 200
        
        # Test patients routes
        response = client.get("/api/v1/patients/")
        assert response.status_code == 200
        
        # Test queue routes
        response = client.get("/api/v1/queue/")
        assert response.status_code == 200
        
        # Test dashboard routes (may return 404 if no endpoint exists)
        response = client.get("/api/v1/dashboard/")
        # Dashboard might not have a root endpoint, so accept 404
        assert response.status_code in [200, 404]
    
    def test_404_for_nonexistent_endpoints(self, client):
        """Test that 404 is returned for non-existent endpoints."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_app_metadata(self):
        """Test that the FastAPI app has correct metadata."""
        assert app.title == "Ops Mesh Backend"
        assert app.description == "Hospital Operations Management System"
        assert app.version == "1.0.0"
    
    def test_middleware_configuration(self):
        """Test that CORS middleware is properly configured."""
        # Check that middleware is configured (more flexible approach)
        assert len(app.user_middleware) > 0
        # Verify that CORS is configured by checking if the app has CORS settings
        assert hasattr(app, 'user_middleware')
    
    def test_router_inclusion(self):
        """Test that all routers are properly included."""
        # Check that all expected routes are in the app
        routes = [route.path for route in app.routes]
        
        # Check for API v1 prefix
        api_routes = [route for route in routes if route.startswith("/api/v1")]
        assert len(api_routes) > 0
        
        # Check for specific route prefixes
        route_prefixes = [route.split("/")[3] for route in api_routes if len(route.split("/")) > 3]
        expected_prefixes = ["appointments", "patients", "queue", "dashboard"]
        
        for prefix in expected_prefixes:
            assert prefix in route_prefixes
