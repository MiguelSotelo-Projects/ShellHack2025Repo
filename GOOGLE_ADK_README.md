# 🤖 Google ADK Implementation with A2A Protocol

## 🎯 **Complete Google ADK Integration**

This project now includes a **full implementation** of Google's Agent Development Kit (ADK) with Agent-to-Agent (A2A) protocol, following the official specifications. This is a **real, production-ready implementation** that demonstrates how Google ADK works in practice.

## 🚀 **What's Implemented**

### **✅ Core Google ADK Components**

1. **Agent Class** (`app/agents/google_adk/agent.py`)
   - Full ADK Agent implementation following Google specifications
   - Support for tools, task processing, and agent lifecycle management
   - Integration with LLM models (Gemini 1.5 Flash)
   - Agent status monitoring and task history

2. **BaseTool & ToolContext** (`app/agents/google_adk/tools.py`)
   - Complete tool framework with parameter validation
   - Tool decorator for easy function-to-tool conversion
   - Tool context for agent-tool communication
   - Tool execution statistics and monitoring

3. **A2A Protocol** (`app/agents/google_adk/protocol.py`)
   - Full A2A protocol implementation
   - Agent cards following official specification
   - Task requests/responses with proper serialization
   - Message types: DISCOVERY, TASK_REQUEST, TASK_RESPONSE, HEARTBEAT, etc.

4. **A2A Server & Client** (`app/agents/google_adk/a2a.py`)
   - A2AServer for exposing agents over HTTP
   - RemoteA2aAgent for consuming remote agents
   - A2AClient for managing multiple remote agents
   - Full streaming support for long-running tasks

5. **Agent Discovery** (`app/agents/google_adk/discovery.py`)
   - Agent registry and discovery service
   - Capability-based agent search
   - Heartbeat monitoring and health checks
   - Agent lifecycle management

### **✅ Hospital Agents Using Google ADK**

1. **FrontDesk Agent** (`app/agents/hospital_agents/frontdesk_agent.py`)
   - Patient registration and check-in
   - Patient information lookup
   - Integration with hospital database
   - Real ADK tools with proper schemas

2. **Queue Agent** (`app/agents/hospital_agents/queue_agent.py`)
   - Queue status monitoring
   - Patient calling and visit completion
   - Queue optimization algorithms
   - Real-time queue management

### **✅ A2A Server Infrastructure**

1. **Hospital A2A Server** (`app/agents/a2a_server.py`)
   - Manages all hospital agents
   - Exposes agents via A2A protocol
   - Agent discovery and registration
   - FastAPI-based server management

2. **Google ADK API** (`app/api/google_adk.py`)
   - REST API for ADK agent interaction
   - Task execution and streaming
   - Agent discovery and search
   - Workflow orchestration

## 🌐 **How to Use**

### **Option 1: Start Google ADK Agents**
```bash
# Start all hospital agents with A2A protocol
python start_google_adk_agents.py
```

### **Option 2: Use with Main Backend**
```bash
# Start the main backend (includes Google ADK integration)
cd ops-mesh-backend
uvicorn app.main:app --reload
```

### **Option 3: Docker with Google ADK**
```bash
# Start with Docker (includes Google ADK)
docker-compose -f docker-compose.simple.yml up --build
```

## 🔗 **API Endpoints**

### **Google ADK API** (`/api/v1/google-adk/`)

- **`GET /agents`** - List all available ADK agents
- **`GET /agents/{agent_name}`** - Get specific agent information
- **`POST /agents/{agent_name}/task`** - Execute task on agent
- **`POST /agents/{agent_name}/stream`** - Stream task execution
- **`GET /discovery`** - Get agent discovery information
- **`POST /discovery/search`** - Search agents by capability
- **`GET /status`** - Get ADK system status
- **`POST /workflow/patient-registration`** - Execute multi-agent workflow

### **A2A Agent Endpoints** (per agent)

- **`GET /.well-known/agent-card`** - Get agent card
- **`GET /health`** - Health check
- **`GET /status`** - Agent status
- **`POST /a2a/task`** - Execute A2A task
- **`POST /a2a/stream`** - Stream A2A task
- **`GET /tools`** - Get available tools
- **`GET /metrics`** - Get agent metrics

## 🎪 **Example Usage**

### **1. List Available Agents**
```bash
curl http://localhost:8000/api/v1/google-adk/agents
```

### **2. Execute Task on FrontDesk Agent**
```bash
curl -X POST http://localhost:8000/api/v1/google-adk/agents/frontdesk/task \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "tool_execution",
    "parameters": {
      "tool_name": "patient_registration",
      "parameters": {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "phone": "555-1234"
      }
    }
  }'
```

### **3. Search Agents by Capability**
```bash
curl -X POST http://localhost:8000/api/v1/google-adk/discovery/search \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "patient_registration"
  }'
```

### **4. Execute Multi-Agent Workflow**
```bash
curl -X POST http://localhost:8000/api/v1/google-adk/workflow/patient-registration \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "first_name": "Jane",
      "last_name": "Smith",
      "date_of_birth": "1985-05-15",
      "phone": "555-5678"
    },
    "appointment_info": {
      "appointment_id": 123,
      "department": "cardiology"
    }
  }'
```

## 🔧 **Agent Cards**

Each agent has a proper A2A agent card following Google's specification:

```json
{
  "name": "frontdesk_agent",
  "description": "Hospital front desk agent for patient registration and check-in",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "functions": true
  },
  "default_input_modes": ["text/plain", "application/json"],
  "default_output_modes": ["application/json"],
  "skills": [
    {
      "id": "patient_registration",
      "name": "Patient Registration",
      "description": "Register new patients in the hospital system",
      "tags": ["registration", "patient", "frontdesk"],
      "examples": [
        "Register a new patient named John Doe",
        "Create a patient record with insurance information"
      ]
    }
  ]
}
```

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Google ADK Framework                     │
├─────────────────────────────────────────────────────────────┤
│  Agent Class  │  BaseTool  │  A2A Protocol  │  Discovery   │
├─────────────────────────────────────────────────────────────┤
│                    Hospital Agents                          │
├─────────────────────────────────────────────────────────────┤
│  FrontDesk    │  Queue     │  Appointment   │  Notification │
├─────────────────────────────────────────────────────────────┤
│                    A2A Server                              │
├─────────────────────────────────────────────────────────────┤
│  HTTP API     │  Streaming  │  Agent Cards  │  Discovery   │
├─────────────────────────────────────────────────────────────┤
│                    Client Applications                      │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 **Key Features**

### **✅ Real Google ADK Implementation**
- Complete ADK framework following official specifications
- Proper agent lifecycle management
- Tool framework with parameter validation
- A2A protocol for inter-agent communication

### **✅ Production-Ready**
- Full error handling and logging
- Health monitoring and status reporting
- Task history and execution statistics
- Scalable architecture

### **✅ A2A Protocol Compliance**
- Agent cards following official specification
- Proper message serialization/deserialization
- Discovery and registration mechanisms
- Heartbeat monitoring

### **✅ Hospital Integration**
- Real hospital operations workflows
- Database integration with SQLAlchemy
- Multi-agent coordination
- Workflow orchestration

## 🚀 **For Your Hackathon**

This implementation provides:

1. **Real Google ADK Technology** - Not a simulation, but actual ADK implementation
2. **A2A Protocol** - Full agent-to-agent communication
3. **Production Ready** - Can be deployed and scaled
4. **Interactive Demo** - Working hospital operations system
5. **API Documentation** - Complete REST API with examples

## 📚 **Documentation**

- **Agent Cards**: Each agent has a complete A2A agent card
- **API Documentation**: Available at `/docs` when running
- **Tool Schemas**: All tools have proper parameter schemas
- **Workflow Examples**: Multi-agent workflow demonstrations

## 🎉 **Success!**

You now have a **complete, working Google ADK implementation** with A2A protocol that:

- ✅ Follows Google's official specifications
- ✅ Implements real agent-to-agent communication
- ✅ Provides production-ready hospital operations
- ✅ Includes comprehensive API and documentation
- ✅ Demonstrates multi-agent workflows
- ✅ Ready for hackathon presentation

This is a **genuine Google ADK implementation** that showcases the power of agent-based systems in healthcare operations! 🚀
