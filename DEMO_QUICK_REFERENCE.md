# 🚀 Demo Quick Reference Guide

## 🎯 **Key Demo URLs**
- **Live Dashboard**: http://localhost:3006/live-dashboard
- **ADK Showcase**: http://localhost:3006/adk-showcase  
- **Protocol Demo**: http://localhost:3006/adk-protocol-demo
- **API Documentation**: http://localhost:8000/docs

## 🔧 **Essential Commands**

### **Start the Demo**
```bash
./run_docker_demo.sh
```

### **Test Agent Discovery**
```bash
curl http://localhost:8000/api/v1/google-adk/agents
```

### **Initialize Vertex AI**
```bash
curl -X POST http://localhost:8000/api/v1/vertex-ai/initialize \
  -H "Content-Type: application/json" \
  -d '{"api_key": "AQ.Ab8RN6IjxxUAW5VzdXFCyzTVq-EJRWYHmiq-BnKHRFULi4zyyw"}'
```

### **Test AI Conversation**
```bash
curl -X POST http://localhost:8000/api/v1/vertex-ai/agents/frontdesk/conversation \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me register a new patient"}'
```

## 🎪 **Demo Flow**
1. **Live Dashboard** → Show real-time hospital operations
2. **ADK Showcase** → Demonstrate agent discovery and communication
3. **Protocol Demo** → Deep dive into A2A protocol implementation
4. **API Commands** → Show backend agent interactions
5. **Vertex AI** → Demonstrate AI-enhanced capabilities

## 🏆 **Key Points to Emphasize**
- **Real Google ADK Implementation** (not simulation)
- **Production-ready hospital system**
- **AI-powered optimization**
- **Scalable architecture**
- **Complete A2A protocol compliance**
