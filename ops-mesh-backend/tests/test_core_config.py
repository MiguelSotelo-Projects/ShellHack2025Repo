import pytest
from unittest.mock import patch
from app.core.config import Settings, settings


class TestSettings:
    """Test cases for the Settings configuration class."""
    
    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        test_settings = Settings()
        
        assert test_settings.database_url == "sqlite:///./ops_mesh.db"
        assert test_settings.api_v1_str == "/api/v1"
        assert test_settings.project_name == "Ops Mesh"
        assert test_settings.redis_url == "redis://localhost:6379"
        assert test_settings.websocket_path == "/ws"
        
        # Test CORS origins
        expected_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]
        assert test_settings.backend_cors_origins == expected_origins
    
    def test_environment_variable_override(self):
        """Test that environment variables can override default values."""
        with patch.dict('os.environ', {
            'DATABASE_URL': 'postgresql://test:test@localhost/testdb',
            'PROJECT_NAME': 'Test Project',
            'API_V1_STR': '/api/v2',
            'REDIS_URL': 'redis://test:6379'
        }):
            test_settings = Settings()
            
            assert test_settings.database_url == 'postgresql://test:test@localhost/testdb'
            assert test_settings.project_name == 'Test Project'
            assert test_settings.api_v1_str == '/api/v2'
            assert test_settings.redis_url == 'redis://test:6379'
    
    def test_cors_origins_environment_override(self):
        """Test that CORS origins can be overridden via environment variables."""
        with patch.dict('os.environ', {
            'BACKEND_CORS_ORIGINS': '["https://example.com", "https://test.com"]'
        }):
            test_settings = Settings()
            assert test_settings.backend_cors_origins == ["https://example.com", "https://test.com"]
    
    def test_config_class_attributes(self):
        """Test that the Config class has the correct attributes."""
        test_settings = Settings()
        
        assert hasattr(test_settings.Config, 'env_file')
        assert test_settings.Config.env_file == ".env"
    
    def test_settings_singleton(self):
        """Test that the settings instance is properly configured."""
        assert isinstance(settings, Settings)
        assert settings.project_name == "Ops Mesh"
        assert settings.database_url == "sqlite:///./ops_mesh.db"
    
    def test_validation_errors(self):
        """Test that invalid configuration values raise appropriate errors."""
        from pydantic_settings.sources import SettingsError
        
        # Test with invalid environment variable format
        with patch.dict('os.environ', {
            'BACKEND_CORS_ORIGINS': 'invalid_json_format',  # Invalid JSON format
        }):
            # This should raise a SettingsError for invalid JSON
            with pytest.raises(SettingsError):
                Settings()
    
    def test_optional_fields(self):
        """Test that optional fields can be None or empty."""
        test_settings = Settings()
        
        # These should not raise errors even if not set
        assert test_settings.database_url is not None
        assert test_settings.api_v1_str is not None
        assert test_settings.project_name is not None
