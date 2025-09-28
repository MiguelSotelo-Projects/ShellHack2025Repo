from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./ops_mesh.db"
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Ops Mesh Backend"
    
    # CORS
    backend_cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # Redis (for future agent communication)
    redis_url: str = "redis://localhost:6379"
    
    # WebSocket
    websocket_path: str = "/ws"
    
    # Google Cloud Configuration
    google_cloud_project: Optional[str] = None
    google_cloud_region: str = "us-central1"
    google_application_credentials: Optional[str] = None
    
    # Ops Mesh Configuration
    ops_mesh_topic_prefix: str = "ops-mesh"
    ops_mesh_monitoring: bool = True
    ops_mesh_logging: bool = True
    
    # Development Settings
    debug: bool = False
    reload: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()

