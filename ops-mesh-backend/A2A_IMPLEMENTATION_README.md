# A2A Implementation Guide for Ops Mesh

This document provides a comprehensive guide to the A2A (Agent-to-Agent) implementation in the Ops Mesh hospital operations management system.

## 🏗️ Architecture Overview

The A2A implementation consists of several key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ADK Tools     │    │  A2A Protocol   │    │ Discovery       │
│                 │◄──►│                 │◄──►│ Service         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent Cards   │    │ Agent Manager   │    │ Agent Registry  │
│   (JSON)        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
ops-mesh-backend/
├── agents/
│   ├── frontdesk_agent.json          # Agent card for FrontDesk Agent
│   ├── queue_agent.json              # Agent card for Queue Agent
│   ├── appointment_agent.json        # Agent card for Appointment Agent
│   ├── notification_agent.json       # Agent card for Notification Agent
│   ├── orchestrator_agent.json       # Agent card for Orchestrator Agent
│   └── ...
├── app/agents/
│   ├── protocol/
│   │   ├── a2a_protocol.py           # A2A protocol implementation
│   │   └── agent_protocol.py         # Legacy protocol (deprecated)
│   ├── discovery_service.py          # Agent discovery service
│   ├── adk_tools.py                  # ADK tool implementations
│   ├── agent_manager.py              # Agent manager with A2A support
│   └── specialized/
│       ├── frontdesk_agent.py        # Updated FrontDesk Agent
│       ├── queue_agent.py            # Updated Queue Agent
│       ├── appointment_agent.py      # Updated Appointment Agent
│       ├── notification_agent.py     # Updated Notification Agent
│       └── orchestrator_agent.py     # Updated Orchestrator Agent
├── setup_a2a.py                      # A2A server setup script
├── test_a2a_implementation.py        # A2A implementation tests
└── A2A_IMPLEMENTATION_README.md      # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ops-mesh-backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Set your Google Cloud Project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Optional: Set other A2A configuration
export A2A_SERVER_MODE=true
export A2A_DISCOVERY_ENABLED=true
```

### 3. Set Up A2A Environment

```bash
python setup_a2a.py --setup
```

This will:
- Generate A2A configuration files
- Create startup scripts
- Validate agent cards

### 4. Start A2A Server

```bash
python setup_a2a.py --start
```

Or use the generated startup script:

```bash
./start_a2a_server.sh
```

### 5. Test the Implementation

```bash
python test_a2a_implementation.py
```

## 🔧 Configuration

### Agent Cards

Each agent has a JSON card that describes its capabilities:

```json
{
  "name": "frontdesk_agent",
  "version": "1.0.0",
  "description": "Handles patient registration and check-in",
  "capabilities": [
    "patient_registration",
    "patient_check_in",
    "patient_verification",
    "appointment_lookup"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["register_patient", "check_in_patient"]
      }
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "patient_id": {"type": "string"}
    }
  },
  "dependencies": ["queue_agent", "notification_agent"]
}
```

### A2A Configuration

The A2A configuration is generated in `a2a_config.json`:

```json
{
  "a2a_server": {
    "project_id": "your-project-id",
    "region": "us-central1",
    "agents": {
      "frontdesk_agent": {
        "port": 8001,
        "agent_card": "ops-mesh-backend/agents/frontdesk_agent.json",
        "capabilities": ["patient_registration", "patient_check_in"]
      }
    }
  }
}
```

## 🤖 Agent Implementation

### A2A Protocol

The A2A protocol is implemented in `app/agents/protocol/a2a_protocol.py`:

```python
from agents.protocol.a2a_protocol import A2AProtocol, A2ATaskRequest

class MyAgent:
    def __init__(self):
        self.protocol = A2AProtocol(
            "my_agent", 
            "path/to/agent.json"
        )
    
    async def initialize(self):
        await self.protocol.start()
        self.protocol.register_task_handler("my_action", self._handle_my_action)
    
    async def _handle_my_action(self, data):
        # Handle the task
        return {"success": True, "result": "processed"}
```

### Task Communication

Agents communicate using task requests and responses:

```python
# Send a task to another agent
task_id = await self.protocol.send_task_request(
    recipient_id="queue_agent",
    action="add_to_queue",
    data={"patient_id": "PAT-001", "priority": "high"}
)

# Handle incoming tasks
self.protocol.register_task_handler("add_to_queue", self._handle_add_to_queue)
```

## 🔍 Discovery Service

The discovery service manages agent registration and capability discovery:

```python
from agents.discovery_service import discovery_service

# Discover available agents
agents = await discovery_service.discover_agents()

# Find agents with specific capabilities
matching_agents = await discovery_service.find_agents_by_capability("patient_registration")

# Check agent health
is_healthy = await discovery_service.check_agent_health("frontdesk_agent")
```

## 🛠️ ADK Tools

The system provides several ADK tools for agent interaction:

### Agent Discovery Tool

```python
from agents.adk_tools import AgentDiscoveryTool

tool = AgentDiscoveryTool()
result = await tool.execute({
    "action": "discover_agents"
})
```

### A2A Communication Tool

```python
from agents.adk_tools import A2ACommunicationTool

tool = A2ACommunicationTool()
result = await tool.execute({
    "action": "send_task",
    "recipient_id": "queue_agent",
    "action": "add_to_queue",
    "data": {"patient_id": "PAT-001"}
})
```

### Hospital Operations Tool

```python
from agents.adk_tools import HospitalOperationsTool

tool = HospitalOperationsTool()
result = await tool.execute({
    "operation": "get_system_status"
})
```

## 🔄 Workflow Orchestration

The system supports complex multi-agent workflows:

```python
from agents.protocol.a2a_protocol import A2AWorkflowOrchestrator

orchestrator = A2AWorkflowOrchestrator(protocol)

workflow_definition = {
    "type": "patient_flow",
    "steps": [
        {
            "step": 1,
            "action": "register_patient",
            "target_agent": "frontdesk_agent",
            "data": {"patient_data": {...}}
        },
        {
            "step": 2,
            "action": "add_to_queue",
            "target_agent": "queue_agent",
            "data": {"patient_id": "PAT-001"}
        }
    ]
}

workflow_id = await orchestrator.start_workflow("patient_flow_001", workflow_definition)
```

## 🧪 Testing

### Running Tests

```bash
# Run all A2A tests
python test_a2a_implementation.py

# Run specific test categories
python -m pytest tests/test_a2a_protocol.py
python -m pytest tests/test_discovery_service.py
```

### Test Coverage

The test suite covers:
- Discovery service functionality
- Agent registration and card loading
- Agent manager operations
- ADK tools functionality
- A2A communication protocol
- End-to-end workflow execution

## 📊 Monitoring

### Agent Health Monitoring

The discovery service monitors agent health through heartbeats:

```python
# Check agent health
is_healthy = await discovery_service.check_agent_health("frontdesk_agent")

# Get discovery statistics
stats = await discovery_service.get_discovery_stats()
```

### System Status

Monitor overall system status:

```python
from agents.adk_tools import HospitalOperationsTool

tool = HospitalOperationsTool()
status = await tool.execute({"operation": "get_system_status"})
```

## 🔒 Security

### Authentication

The A2A protocol includes authentication mechanisms:

```python
from agents.protocol.a2a_protocol import A2ASecurity

security = A2ASecurity()
authenticated = await security.authenticate_agent("agent_id", "credentials")
```

### Agent Validation

Agents are validated through their agent cards and capabilities.

## 🚨 Troubleshooting

### Common Issues

1. **Agent Registration Fails**
   - Check if agent card exists and is valid JSON
   - Verify agent capabilities are properly defined
   - Ensure discovery service is running

2. **Task Communication Fails**
   - Verify recipient agent is available
   - Check agent capabilities match task requirements
   - Review A2A protocol logs

3. **Discovery Service Issues**
   - Check if discovery service is started
   - Verify agent heartbeats are being received
   - Review discovery service logs

### Debug Mode

Enable debug logging:

```bash
export A2A_DEBUG=true
python setup_a2a.py --start
```

### Logs

Check logs for detailed information:
- Agent logs: `logs/agents/`
- Discovery service logs: `logs/discovery/`
- A2A protocol logs: `logs/a2a/`

## 📈 Performance

### Optimization Tips

1. **Agent Pooling**: Use agent pools for high-volume operations
2. **Task Batching**: Batch related tasks for efficiency
3. **Caching**: Cache agent capabilities and discovery results
4. **Monitoring**: Monitor agent performance and health

### Scaling

The A2A implementation supports horizontal scaling:
- Multiple agent instances
- Load balancing across agents
- Distributed task processing

## 🔮 Future Enhancements

### Planned Features

1. **Advanced Workflow Engine**: More sophisticated workflow orchestration
2. **Agent Learning**: Agents that learn from interactions
3. **Real-time Analytics**: Live monitoring and analytics
4. **Multi-region Support**: Cross-region agent communication
5. **Enhanced Security**: Advanced authentication and authorization

### Integration Opportunities

1. **External Systems**: Integration with external hospital systems
2. **AI/ML Services**: Integration with AI/ML services
3. **IoT Devices**: Integration with IoT medical devices
4. **Mobile Apps**: Mobile app integration

## 📚 API Reference

### A2A Protocol Classes

- `A2AProtocol`: Main protocol implementation
- `A2ATaskRequest`: Task request structure
- `A2ATaskResponse`: Task response structure
- `A2AWorkflowOrchestrator`: Workflow orchestration

### Discovery Service

- `AgentDiscoveryService`: Main discovery service
- `AgentInfo`: Agent information structure

### ADK Tools

- `AgentDiscoveryTool`: Agent discovery operations
- `A2ACommunicationTool`: A2A communication operations
- `HospitalOperationsTool`: Hospital operations management

## 🤝 Contributing

### Development Guidelines

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update agent cards when adding capabilities
4. Document new A2A protocol features
5. Follow Google ADK best practices

### Adding New Agents

1. Create agent card JSON file
2. Implement agent class with A2A protocol
3. Add agent to agent manager
4. Create tests for the agent
5. Update documentation

## 📄 License

This A2A implementation is part of the Ops Mesh project and follows the same license terms.

---

**Built with ❤️ for better healthcare operations using A2A protocol**
