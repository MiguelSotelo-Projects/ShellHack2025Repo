from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from .core.config import settings
from .core.database import engine, Base
from .api import appointments, patients, queue, dashboard, walkin, checkin
from .websockets import dashboard_ws

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    description="Hospital Operations Management System",
    version="1.0.0",
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    appointments.router,
    prefix=f"{settings.api_v1_str}/appointments",
    tags=["appointments"]
)

app.include_router(
    patients.router,
    prefix=f"{settings.api_v1_str}/patients",
    tags=["patients"]
)

app.include_router(
    queue.router,
    prefix=f"{settings.api_v1_str}/queue",
    tags=["queue"]
)

app.include_router(
    dashboard.router,
    prefix=f"{settings.api_v1_str}/dashboard",
    tags=["dashboard"]
)

app.include_router(
    walkin.router,
    prefix=f"{settings.api_v1_str}/walkin",
    tags=["walkin"]
)

app.include_router(
    checkin.router,
    prefix=f"{settings.api_v1_str}/checkin",
    tags=["checkin"]
)

# Include WebSocket routers
app.include_router(
    dashboard_ws.router,
    prefix=f"{settings.api_v1_str}/ws",
    tags=["websockets"]
)


@app.get("/")
def read_root():
    return {
        "message": "Ops Mesh API",
        "version": "1.0.0",
        "docs": "/docs",
        "api": settings.api_v1_str
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ops-mesh-backend"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

