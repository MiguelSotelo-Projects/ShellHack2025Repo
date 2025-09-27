from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./ops_mesh.db"
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Ops Mesh"
    
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
    
    class Config:
        env_file = ".env"


settings = Settings()

