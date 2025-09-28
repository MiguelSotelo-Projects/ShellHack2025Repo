# 🤝 Collaborator Guide - ShellHacks 2025

Welcome to the ShellHacks 2025 project! This guide will help you get the demo running quickly.

## 🚀 Quick Start (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- Git installed

### 1. Clone the Repository
```bash
git clone https://github.com/MiguelSotelo-Projects/ShellHack2025Repo.git
cd ShellHack2025Repo
```

### 2. Run the Demo
```bash
# One command to rule them all!
docker-compose -f docker-compose.simple.yml up --build
```

That's it! 🎉 The demo will be available at:
- **Main Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 🐳 Docker Commands

```bash
# Start demo (background)
docker-compose -f docker-compose.simple.yml up -d

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Stop demo
docker-compose -f docker-compose.simple.yml down

# Restart demo
docker-compose -f docker-compose.simple.yml restart

# Check status
docker-compose -f docker-compose.simple.yml ps
```

## 🌐 Available Features

Once running, you can access:

- **🏠 Main Dashboard**: http://localhost:3000
- **✨ Enhanced Dashboard**: http://localhost:3000/enhanced-dashboard
- **🤖 Agent Demo**: http://localhost:3000/agent-demo
- **📊 Live Dashboard**: http://localhost:3000/live-dashboard
- **👥 Patient Flow**: http://localhost:3000/patient-flow
- **📚 API Documentation**: http://localhost:8000/docs
- **❤️ Health Check**: http://localhost:8000/health

## 🔧 Development Setup (Alternative)

If you prefer local development without Docker:

```bash
# Backend setup
cd ops-mesh-backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend setup (in another terminal)
cd ops-mesh-frontend
npm install
npm run dev
```

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Find and kill processes on ports 8000/3000
lsof -ti:8000,3000 | xargs kill -9
```

### Docker Issues
```bash
# Clean restart
docker-compose -f docker-compose.simple.yml down
docker-compose -f docker-compose.simple.yml up --build
```

### Permission Issues (Linux/macOS)
```bash
# Make scripts executable
chmod +x run_docker_demo.sh
chmod +x docker-entrypoint.sh
```

## 📁 Project Structure

```
ShellHack2025Repo/
├── ops-mesh-backend/          # FastAPI backend
├── ops-mesh-frontend/         # Next.js frontend
├── docker-compose.simple.yml  # Docker setup
├── Dockerfile.simple          # Docker configuration
├── run_docker_demo.sh         # Helper script
└── README.md                  # Main documentation
```

## 🎯 What This Demo Shows

- **Agent-to-Agent (A2A) Communication**: Multi-agent coordination
- **Hospital Operations**: Patient management and queue systems
- **Real-time Monitoring**: Live dashboards and status updates
- **API Integration**: RESTful APIs with FastAPI
- **Modern Frontend**: React/Next.js with real-time updates

## 💡 Tips for Collaborators

1. **Use Docker**: It's the easiest way to get started
2. **Check Logs**: Use `docker-compose logs -f` to see what's happening
3. **Port Conflicts**: Make sure ports 8000 and 3000 are free
4. **Data Persistence**: Database data is saved in `./data/` directory
5. **Hot Reload**: Frontend supports hot reloading in development mode

## 🆘 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review [DOCKER_README.md](DOCKER_README.md) for Docker-specific information
- Look at the API documentation at http://localhost:8000/docs when running

Happy coding! 🚀
