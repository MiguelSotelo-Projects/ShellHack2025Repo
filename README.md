# ShellHacks2025 - Google ADK/A2A Protocol Demo

A comprehensive hospital operations management system demonstrating **Google's ADK (Agent Development Kit)** and **Agent-to-Agent (A2A) communication protocols** in a real-world healthcare environment.

## 🎯 **Hackathon Showcase**

**🤖 [ADK Showcase](http://localhost:3000/adk-showcase)** - Interactive demonstration of Google ADK capabilities  
**🔗 [Protocol Demo](http://localhost:3000/adk-protocol-demo)** - Deep dive into A2A protocol implementation  
**⚡ [Hybrid Agents](http://localhost:3000/hybrid-agents)** - Real + Simulated agent communication  
**📊 [Live Dashboard](http://localhost:3000/live-dashboard)** - Real-time agent monitoring and communication

## 🚀 Quick Start

### 🐳 Docker Setup (Recommended - No Dependencies!)

**For New Collaborators:**
```bash
git clone https://github.com/MiguelSotelo-Projects/ShellHack2025Repo.git
cd ShellHack2025Repo
docker-compose -f docker-compose.simple.yml up --build
```

**Windows:**
```cmd
run_docker_demo.bat
```

**macOS/Linux:**
```bash
./run_docker_demo.sh
```

**Docker Compose:**
```bash
docker-compose -f docker-compose.simple.yml up --build
```

### 🔧 Local Setup (Requires Python & Node.js)

**Windows:**
```cmd
run_demo.bat
```

**macOS/Linux:**
```bash
./run_demo.sh
```

**Cross-Platform:**
```bash
python run_full_demo.py
```

## 📋 What's Included

### **🤖 Google ADK Integration**
- **Complete Google ADK Implementation** following official specifications
- **A2A Protocol** for secure agent-to-agent communication
- **Multi-agent coordination** with workflow orchestration
- **Real-time agent discovery** and capability matching
- **Production-ready hospital agents** with proper tool frameworks

### **🏥 Hospital Operations System**
- **Complete Demo Runner**: Automated setup and execution
- **Backend API**: FastAPI with A2A protocol implementation
- **Frontend Dashboard**: Next.js with real-time monitoring
- **Agent System**: Multi-agent communication and coordination
- **Patient Management**: Registration, appointments, and queue management

### **🎪 Interactive Demonstrations**
- **Agent Discovery**: Real-time agent registration and capability discovery
- **A2A Communication**: Live agent-to-agent messaging visualization
- **Workflow Orchestration**: Multi-agent patient registration workflows
- **Security Monitoring**: Real-time security and authentication status
- **Performance Metrics**: Live protocol performance and statistics

## 🌐 Demo URLs

Once running:
- **🤖 ADK Showcase**: http://localhost:3000/adk-showcase
- **🔗 Protocol Demo**: http://localhost:3000/adk-protocol-demo
- **⚡ Hybrid Agents**: http://localhost:3000/hybrid-agents
- **📊 Live Dashboard**: http://localhost:3000/live-dashboard
- **🏥 Main Dashboard**: http://localhost:3000
- **📚 API Docs**: http://localhost:8000/docs

## 📚 Documentation

- **[🤖 Google ADK Implementation](GOOGLE_ADK_README.md)** - Complete Google ADK with A2A protocol
- **[🤖 ADK Demo Guide](ADK_DEMO_README.md)** - Interactive demonstration guide
- [Complete Demo Runner Guide](DEMO_RUNNER_README.md)
- [Docker Setup Guide](DOCKER_README.md)
- [Collaborator Guide](COLLABORATOR_GUIDE.md)

## 🎯 Features

- Real-time agent status monitoring
- Patient flow management
- Queue optimization
- A2A protocol workflow testing
- Multi-agent coordination

## 🛠️ Technical Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: Next.js, React, TypeScript
- **Database**: SQLite
- **Agents**: Custom A2A protocol implementation

---

**Ready for ShellHacks 2025! 🎉**
