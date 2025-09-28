# 🤖 Google ADK/A2A Protocol Demonstration

## 🎯 **Hackathon Showcase Overview**

This project demonstrates the power of **Google's ADK (Agent Development Kit)** and **A2A (Agent-to-Agent) protocol** in a real-world hospital operations management system. Built for ShellHacks 2025, this showcase highlights how multiple AI agents can work together seamlessly to manage complex healthcare workflows.

## 🚀 **Quick Start - See the ADK in Action**

### **Option 1: Docker (Recommended)**
```bash
git clone https://github.com/MiguelSotelo-Projects/ShellHack2025Repo.git
cd ShellHack2025Repo
docker-compose -f docker-compose.simple.yml up --build
```

### **Option 2: Local Development**
```bash
# Backend
cd ops-mesh-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd ops-mesh-frontend
npm install
npm run dev
```

## 🌐 **Access the ADK Demonstrations**

Once running, visit these URLs to see the ADK in action:

- **🤖 [ADK Showcase](http://localhost:3000/adk-showcase)** - Main demonstration page
- **🔗 [Protocol Demo](http://localhost:3000/adk-protocol-demo)** - Deep dive into A2A protocol
- **📊 [Live Dashboard](http://localhost:3000/live-dashboard)** - Real-time agent monitoring
- **🏥 [Hospital View](http://localhost:3000/hospital)** - Complete hospital operations

## 🎪 **What You'll See**

### **1. Agent Discovery & Registration**
- **Real-time agent discovery** using A2A protocol
- **Capability matching** and service registration
- **Health monitoring** with heartbeat systems
- **Security authentication** and certificate validation

### **2. Multi-Agent Communication**
- **Agent-to-Agent messaging** with real-time visualization
- **Task distribution** and workflow coordination
- **Message routing** and delivery confirmation
- **Error handling** and retry mechanisms

### **3. Workflow Orchestration**
- **Complex patient workflows** managed by multiple agents
- **Parallel task execution** with dependency management
- **Real-time progress tracking** and status updates
- **Automatic error recovery** and fallback procedures

### **4. Security & Authentication**
- **End-to-end encryption** for all agent communications
- **Certificate-based authentication** for agent identity
- **Rate limiting** and security monitoring
- **Audit logging** for compliance and debugging

## 🤖 **Agent Ecosystem**

### **Core Agents**

| Agent | Purpose | Capabilities |
|-------|---------|--------------|
| **Orchestrator** | Workflow coordination | Task distribution, error handling, security monitoring |
| **Front Desk** | Patient registration | Check-in, data validation, info updates |
| **Queue Manager** | Queue optimization | Wait time calculation, patient calling, optimization |
| **Appointment** | Scheduling | Booking, rescheduling, conflict resolution |
| **Notification** | Communications | SMS, email, push notifications, delivery tracking |

### **Agent Capabilities**

Each agent exposes specific capabilities through the A2A protocol:

```json
{
  "agent_id": "frontdesk_agent",
  "capabilities": [
    "register_patient",
    "check_in_patient", 
    "update_patient_info",
    "validate_patient_data"
  ],
  "protocol_version": "A2A-v1.2",
  "security_level": "high"
}
```

## 🔧 **Technical Implementation**

### **Backend Architecture**
- **FastAPI** with async/await for high performance
- **Google ADK** integration with fallback implementations
- **A2A Protocol** for agent communication
- **SQLAlchemy** for data persistence
- **Real-time WebSocket** connections

### **Frontend Features**
- **React/Next.js** with TypeScript
- **Real-time updates** using WebSocket connections
- **Interactive visualizations** of agent networks
- **Live monitoring** of protocol messages
- **Responsive design** for all devices

### **Key ADK Features Demonstrated**

1. **Agent Discovery Service**
   ```python
   # Automatic agent registration and capability discovery
   discovery_service.register_agent(agent_id, capabilities)
   available_agents = discovery_service.find_agents_by_capability("patient_registration")
   ```

2. **A2A Protocol Communication**
   ```python
   # Secure agent-to-agent messaging
   protocol = A2AProtocol(agent_id, agent_config)
   response = await protocol.send_task_request(target_agent, task_data)
   ```

3. **Workflow Orchestration**
   ```python
   # Multi-agent workflow coordination
   orchestrator = OrchestratorAgent()
   workflow_result = await orchestrator.execute_workflow(workflow_definition)
   ```

## 📊 **Live Demonstrations**

### **Patient Registration Workflow**
1. **Front Desk Agent** receives patient information
2. **Orchestrator Agent** coordinates the workflow
3. **Queue Agent** adds patient to appropriate queue
4. **Appointment Agent** schedules follow-up if needed
5. **Notification Agent** sends confirmation to patient

### **Real-time Monitoring**
- **Agent status** and health monitoring
- **Message flow** visualization
- **Performance metrics** and statistics
- **Error tracking** and debugging

## 🎯 **Hackathon Highlights**

### **What Makes This Special**
- **Real-world application** in healthcare operations
- **Complete A2A implementation** with all protocol features
- **Interactive demonstrations** that judges can try
- **Production-ready code** with proper error handling
- **Comprehensive documentation** and setup instructions

### **Google ADK Features Showcased**
- ✅ **Agent Development Kit** integration
- ✅ **A2A Protocol** implementation
- ✅ **Multi-agent coordination** and communication
- ✅ **Security and authentication** features
- ✅ **Real-time monitoring** and debugging
- ✅ **Workflow orchestration** capabilities

## 🛠️ **Development Setup**

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- Docker (optional but recommended)

### **Backend Setup**
```bash
cd ops-mesh-backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### **Frontend Setup**
```bash
cd ops-mesh-frontend
npm install
npm run dev
```

### **Database Setup**
```bash
# The application will automatically create the database and tables
# No manual setup required
```

## 📱 **Mobile-Friendly**

The demonstration is fully responsive and works on:
- **Desktop browsers** (Chrome, Firefox, Safari, Edge)
- **Tablets** (iPad, Android tablets)
- **Mobile phones** (iOS, Android)

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Port conflicts**: Make sure ports 8000 and 3000 are free
   ```bash
   lsof -ti:8000,3000 | xargs kill -9
   ```

2. **Docker issues**: Clean restart
   ```bash
   docker-compose -f docker-compose.simple.yml down
   docker-compose -f docker-compose.simple.yml up --build
   ```

3. **Permission issues** (Linux/macOS):
   ```bash
   chmod +x run_docker_demo.sh
   chmod +x docker-entrypoint.sh
   ```

## 🎉 **Demo Script for Judges**

### **5-Minute Demo Flow**
1. **Start with ADK Showcase** - Show agent discovery and capabilities
2. **Run Patient Workflow** - Demonstrate multi-agent coordination
3. **Show Protocol Demo** - Deep dive into A2A communication
4. **Live Monitoring** - Real-time agent status and message flow
5. **Mobile Demo** - Show responsive design on phone/tablet

### **Key Talking Points**
- **Real-world application** in healthcare
- **Google ADK integration** with proper fallbacks
- **A2A protocol** implementation with security
- **Multi-agent coordination** for complex workflows
- **Production-ready code** with comprehensive error handling

## 📞 **Support**

For questions or issues:
- **GitHub Issues**: [Create an issue](https://github.com/MiguelSotelo-Projects/ShellHack2025Repo/issues)
- **Documentation**: Check the main [README.md](README.md)
- **Docker Setup**: See [DOCKER_README.md](DOCKER_README.md)

---

**Built with ❤️ for ShellHacks 2025 - Demonstrating the power of Google ADK and A2A Protocol in real-world applications!**
