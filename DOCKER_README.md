# 🐳 Docker Setup - ShellHacks 2025

This repository now includes a complete Docker setup that eliminates the need for virtual environments and dependency management. Everything runs in isolated containers!

## 🚀 Quick Start with Docker

### Option 1: One-Click Docker Run (Recommended)

**Windows:**
```cmd
run_docker_demo.bat
```

**macOS/Linux:**
```bash
./run_docker_demo.sh
```

### Option 2: Docker Compose Commands

```bash
# Build and start the demo
docker-compose up --build

# Run in background
docker-compose up -d

# Stop the demo
docker-compose down
```

## 📋 What Docker Provides

### ✅ **Complete Isolation**
- No need for Python virtual environments
- No Node.js version conflicts
- No dependency management issues
- Consistent environment across all systems

### ✅ **Automatic Setup**
- Multi-stage build optimizes image size
- All dependencies pre-installed
- Database automatically initialized
- Both frontend and backend start together

### ✅ **Easy Management**
- Single command to start everything
- Health checks ensure services are running
- Persistent data storage
- Easy cleanup and restart

## 🏗️ Docker Architecture

### **Multi-Stage Build Process:**

1. **Frontend Builder Stage**: Builds the Next.js application
2. **Backend Stage**: Installs Python dependencies
3. **Production Stage**: Combines everything into a single optimized image

### **Services:**
- **Backend**: FastAPI server on port 8000
- **Frontend**: Next.js server on port 3000
- **Database**: SQLite with persistent volume
- **Health Checks**: Automatic service monitoring

## 🌐 Access Your Demo

Once running, access your demo at:

- **🏠 Main Dashboard**: http://localhost:3000
- **✨ Enhanced Dashboard**: http://localhost:3000/enhanced-dashboard
- **🤖 Agent Demo**: http://localhost:3000/agent-demo
- **📊 Live Dashboard**: http://localhost:3000/live-dashboard
- **👥 Patient Flow**: http://localhost:3000/patient-flow
- **📚 API Documentation**: http://localhost:8000/docs
- **❤️ Health Check**: http://localhost:8000/health

## 🛠️ Docker Commands

### **Basic Operations:**
```bash
# Start the demo
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the demo
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up --build
```

### **Development Commands:**
```bash
# Access container shell
docker-compose exec ops-mesh-demo bash

# View container status
docker-compose ps

# Check service health
docker-compose exec ops-mesh-demo curl http://localhost:8000/health
```

### **Cleanup Commands:**
```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove containers, volumes, and images
docker-compose down -v --rmi all
```

## 📁 File Structure

```
ShellHack2025Repo/
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Docker Compose configuration
├── docker-entrypoint.sh       # Container startup script
├── .dockerignore             # Files to exclude from build
├── run_docker_demo.sh        # Unix/Linux Docker runner
├── run_docker_demo.bat       # Windows Docker runner
├── DOCKER_README.md          # This file
├── data/                     # Persistent database storage
├── ops-mesh-backend/         # Backend source code
└── ops-mesh-frontend/        # Frontend source code
```

## 🔧 Configuration

### **Environment Variables:**
- `DATABASE_URL`: SQLite database path
- `API_V1_STR`: API version prefix
- `PROJECT_NAME`: Application name
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins
- `DEBUG`: Debug mode (false in production)
- `RELOAD`: Auto-reload (false in production)

### **Ports:**
- **8000**: Backend API server
- **3000**: Frontend web server

### **Volumes:**
- `./data:/app/data`: Persistent database storage

## 🚨 Troubleshooting

### **Port Already in Use:**
```bash
# Check what's using the ports
lsof -i:8000,3000

# Kill processes using the ports
lsof -ti:8000,3000 | xargs kill -9
```

### **Docker Build Issues:**
```bash
# Clean build (no cache)
docker-compose build --no-cache

# Remove all containers and images
docker-compose down -v --rmi all
```

### **Service Not Starting:**
```bash
# Check container logs
docker-compose logs ops-mesh-demo

# Check container status
docker-compose ps

# Restart services
docker-compose restart
```

### **Database Issues:**
```bash
# Remove database volume and restart
docker-compose down -v
docker-compose up -d
```

## 🎯 Benefits of Docker Setup

1. **No Environment Setup**: No need to install Python, Node.js, or manage versions
2. **Consistent Experience**: Same environment on Windows, macOS, and Linux
3. **Easy Cleanup**: Remove containers to clean up everything
4. **Isolation**: No conflicts with other projects
5. **Production Ready**: Same container can be deployed anywhere
6. **Team Collaboration**: Everyone gets the exact same environment

## 🔄 Migration from Local Setup

If you were previously using the local setup:

1. **Stop local services**: Kill any running Python/Node processes
2. **Use Docker**: Run `./run_docker_demo.sh` or `run_docker_demo.bat`
3. **Access same URLs**: All the same endpoints work
4. **Data persistence**: Database data is preserved in `./data/` directory

## 🎉 Ready to Demo!

Your Docker setup is now ready! Simply run:

```bash
./run_docker_demo.sh
```

And your entire ShellHacks 2025 demo will be running in isolated containers with no dependency management required!
