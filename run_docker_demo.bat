@echo off
REM ShellHacks 2025 - Windows Docker Demo Runner
REM This script builds and runs the entire demo using Docker

echo 🐳 ShellHacks 2025 - Docker Demo Runner
echo =======================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose and try again.
    pause
    exit /b 1
)

REM Check if Docker daemon is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker daemon is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are available

REM Create data directory if it doesn't exist
if not exist "data" mkdir data

REM Build and start the demo
echo 🔧 Building Docker image...
docker-compose build --no-cache
if errorlevel 1 (
    echo ❌ Failed to build Docker image
    pause
    exit /b 1
)

echo 🚀 Starting the demo...
docker-compose up -d
if errorlevel 1 (
    echo ❌ Failed to start Docker containers
    pause
    exit /b 1
)

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service health...

REM Check backend
:check_backend
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⏳ Backend still starting...
    timeout /t 2 /nobreak >nul
    goto check_backend
)
echo ✅ Backend is ready

REM Check frontend
:check_frontend
curl -f http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo ⏳ Frontend still starting...
    timeout /t 2 /nobreak >nul
    goto check_frontend
)
echo ✅ Frontend is ready

echo.
echo 🎊 Demo is running successfully in Docker!
echo ==========================================
echo 🌐 Available URLs:
echo    • Main Dashboard: http://localhost:3000
echo    • Enhanced Dashboard: http://localhost:3000/enhanced-dashboard
echo    • Agent Demo: http://localhost:3000/agent-demo
echo    • Live Dashboard: http://localhost:3000/live-dashboard
echo    • Patient Flow: http://localhost:3000/patient-flow
echo    • API Documentation: http://localhost:8000/docs
echo    • Health Check: http://localhost:8000/health
echo.
echo 🐳 Docker Commands:
echo    • View logs: docker-compose logs -f
echo    • Stop demo: docker-compose down
echo    • Restart: docker-compose restart
echo    • Shell access: docker-compose exec ops-mesh-demo bash
echo.
echo ✨ Features Available:
echo    • Visual agent status monitoring
echo    • Patient management with status updates
echo    • Queue management with dequeue operations
echo    • Real-time statistics and activity logs
echo    • A2A protocol workflow testing
echo    • Agent-to-agent communication
echo.
echo 🛑 To stop the demo, run: docker-compose down
echo ==========================================
echo.
echo Press any key to continue...
pause >nul
