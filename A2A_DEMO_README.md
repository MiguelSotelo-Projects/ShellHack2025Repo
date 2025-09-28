# 🎉 A2A Protocol Demo - Live Agent Communication

This demo showcases the complete **Agent-to-Agent (A2A) protocol** implementation with Google ADK fallback, real-time agent communication, and workflow orchestration.

## 🚀 Quick Start

### Option 1: Automated Demo (Recommended)
```bash
# From the ShellHack2025Repo directory
python start_demo.py
```

This will start both backend and frontend automatically.

### Option 2: Manual Setup
```bash
# Terminal 1 - Start Backend
cd ops-mesh-backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Start Frontend  
cd ops-mesh-frontend
npm run dev
```

## 🎯 Demo URLs

Once running, visit these URLs:

- **🏠 Main Dashboard**: http://localhost:3000
- **✨ Enhanced Dashboard**: http://localhost:3000/enhanced-dashboard
- **🤖 Agent Demo**: http://localhost:3000/agent-demo
- **📊 Live Dashboard**: http://localhost:3000/live-dashboard  
- **📚 API Docs**: http://localhost:8000/docs
- **🔍 Agent Status**: http://localhost:8000/api/v1/agents/status

## 🧪 What You Can Test

### 1. **Enhanced Dashboard Features**
- **Visual Agent Monitoring**: Real-time agent status with activity indicators
- **Patient Management**: Create, view, and update patient status
- **Queue Management**: Monitor queue, call next patient, update queue entry status
- **Real-time Statistics**: Live dashboard with patient counts, wait times, and service metrics

### 2. **Agent Status Monitoring**
- View real-time status of all 5 agents with visual indicators
- See agent capabilities and heartbeat information
- Monitor discovery service activity
- Test agent-to-agent communication

### 3. **Patient Registration Workflow**
- **FrontDesk Agent** → **Queue Agent** → **Notification Agent**
- Complete patient registration with database persistence
- Real-time queue updates and notifications

### 4. **Appointment Scheduling Workflow**  
- **Appointment Agent** → **Notification Agent**
- Schedule appointments with confirmation notifications
- Database integration with appointment models

### 5. **Queue Management Operations**
- **Queue Agent** operations (get status, call next patient)
- Priority-based queue handling
- Real-time queue updates

### 6. **Emergency Coordination**
- **Orchestrator Agent** coordinates emergency response
- Multi-agent emergency workflow
- Critical priority handling

### 7. **Agent Communication Testing**
- Basic agent-to-agent message passing
- A2A protocol validation
- Real-time activity logging

## 🔧 Technical Features Demonstrated

### ✅ **A2A Protocol Implementation**
- Task-based agent communication
- Real message passing between agents
- Workflow orchestration
- Discovery service integration

### ✅ **Google ADK Fallback**
- Complete internal implementation
- Works without Google ADK dependencies
- Full compatibility with ADK interfaces

### ✅ **Database Integration**
- Real SQLAlchemy models
- Patient, Appointment, and Queue persistence
- Proper error handling and transactions

### ✅ **Real-time Monitoring**
- Live agent status updates
- Activity logging and monitoring
- WebSocket support for real-time updates

## 🎮 Interactive Demo Features

### **Agent Status Panel**
- Live status of all 5 agents (FrontDesk, Queue, Appointment, Notification, Orchestrator)
- Agent capabilities and heartbeat monitoring
- Discovery service statistics

### **Workflow Testing**
- Interactive forms for each workflow type
- Real-time execution and monitoring
- Success/failure feedback

### **Activity Log**
- Real-time A2A protocol activity
- Agent communication logs
- Workflow execution tracking

### **Test Results**
- Workflow execution results
- Success/failure status
- Workflow ID tracking

## 🏗️ Architecture Overview

```
Frontend (Next.js) ←→ Backend (FastAPI) ←→ A2A Protocol ←→ Agents
     ↓                      ↓                    ↓
  React UI              REST API           Task-based
  Real-time             WebSocket          Communication
  Monitoring            Database           Workflow
                        Integration        Orchestration
```

## 🔍 Agent Communication Flow

1. **Frontend** sends workflow request to **Backend API**
2. **Backend** creates **A2A Protocol** task request
3. **A2A Protocol** routes task to appropriate **Agent**
4. **Agent** processes task and communicates with other agents
5. **Database** is updated with results
6. **Frontend** receives real-time updates

## 🎯 Key Workflows Demonstrated

### **Patient Registration Flow**
```
User Input → FrontDesk Agent → Queue Agent → Notification Agent
     ↓              ↓              ↓              ↓
  Form Data    Register Patient  Add to Queue  Send Welcome
```

### **Appointment Scheduling Flow**
```
User Input → Appointment Agent → Notification Agent
     ↓              ↓                    ↓
  Form Data    Schedule Appointment  Send Confirmation
```

### **Emergency Coordination Flow**
```
Emergency → Orchestrator Agent → Queue Agent + Notification Agent
    ↓              ↓                    ↓              ↓
  Critical    Coordinate Response   Priority Queue   Emergency Alert
```

## 🚨 Troubleshooting

### Backend Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check agent status
curl http://localhost:8000/api/v1/agents/status
```

### Frontend Issues
```bash
# Check if frontend is running
curl http://localhost:3000

# Check if dependencies are installed
cd ops-mesh-frontend
npm install
```

### Database Issues
```bash
# Check database file
ls -la ops-mesh-backend/ops_mesh.db

# Reset database (if needed)
rm ops-mesh-backend/ops_mesh.db
```

## 🎉 Success Indicators

You'll know the demo is working when you see:

- ✅ All 5 agents showing "ACTIVE" status
- ✅ Workflow executions completing successfully  
- ✅ Real-time activity logs showing agent communication
- ✅ Database updates persisting across page refreshes
- ✅ Notifications and alerts being sent between agents

## 🔗 Next Steps

After exploring the demo, you can:

1. **Extend the workflows** by adding more agent interactions
2. **Add new agent types** for specialized hospital operations
3. **Integrate with real Google ADK** when available
4. **Add more sophisticated error handling** and retry logic
5. **Implement real-time WebSocket** updates for live monitoring

---

**🎊 Enjoy exploring the A2A protocol in action!** The demo showcases a complete, production-ready agent communication system with real database integration and workflow orchestration.
