# 🤖 Agent-to-Agent Communication System

This document describes the agent-to-agent communication system implemented for the Ops Mesh hospital operations platform.

## 🏗️ Architecture Overview

The system consists of specialized agents that communicate with each other using Google Cloud Pub/Sub for message passing and coordination:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  FrontDesk      │    │     Queue       │    │  Appointment    │
│     Agent       │◄──►│     Agent       │◄──►│     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Notification   │    │  Orchestrator   │    │   Google Cloud  │
│     Agent       │◄──►│     Agent       │◄──►│     Pub/Sub     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Specialized Agents

### 1. **FrontDesk Agent** (`frontdesk_agent`)
- **Purpose**: Handles patient registration and check-in processes
- **Tools**: Patient Registration Tool
- **Responsibilities**:
  - Register new patients
  - Check in existing patients
  - Coordinate with queue management

### 2. **Queue Agent** (`queue_agent`)
- **Purpose**: Manages patient queues and wait times
- **Tools**: Queue Management Tool
- **Responsibilities**:
  - Add patients to queues
  - Manage queue priorities
  - Calculate wait times
  - Call next patients

### 3. **Appointment Agent** (`appointment_agent`)
- **Purpose**: Handles appointment scheduling and management
- **Tools**: Appointment Management Tool
- **Responsibilities**:
  - Schedule appointments
  - Update appointment details
  - Cancel appointments
  - Coordinate with notification system

### 4. **Notification Agent** (`notification_agent`)
- **Purpose**: Sends notifications and alerts
- **Tools**: Notification Tool
- **Responsibilities**:
  - Send patient notifications
  - Send staff alerts
  - Send reminders
  - Handle emergency notifications

### 5. **Orchestrator Agent** (`orchestrator_agent`)
- **Purpose**: Coordinates complex workflows between agents
- **Tools**: Workflow Orchestration Tool
- **Responsibilities**:
  - Manage multi-step workflows
  - Coordinate agent interactions
  - Handle emergency situations
  - Monitor workflow progress

## 🔄 Communication Protocol

### Message Types
- **REQUEST**: Direct requests between agents
- **RESPONSE**: Responses to requests
- **NOTIFICATION**: Event notifications
- **COORDINATION**: Workflow coordination messages
- **STATUS_UPDATE**: Status updates
- **ERROR**: Error messages

### Message Priority Levels
- **LOW**: Non-urgent messages
- **MEDIUM**: Standard priority
- **HIGH**: Important messages
- **URGENT**: Critical/emergency messages

### Message Format
```json
{
  "message_id": "unique-message-id",
  "sender_id": "agent-id",
  "recipient_id": "target-agent-id",
  "message_type": "request|response|notification|coordination",
  "priority": "low|medium|high|urgent",
  "payload": {
    "action": "specific-action",
    "data": {...}
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "correlation_id": "optional-correlation-id"
}
```

## 🚀 Getting Started

### Prerequisites
1. Google Cloud Project with Pub/Sub API enabled
2. Service account with Pub/Sub permissions
3. Environment variables configured

### Environment Setup
```bash
# Set your Google Cloud project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Set authentication (if using service account)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install Google ADK (if not already installed)
pip install google-adk
```

### Starting the Agent System
```bash
# Start all agents
python start_agents.py

# Or start individual agents
python -m app.agents.specialized.frontdesk_agent
python -m app.agents.specialized.queue_agent
python -m app.agents.specialized.appointment_agent
python -m app.agents.specialized.notification_agent
python -m app.agents.orchestrator_agent
```

### Testing Agent Communication
```bash
# Run the communication test
python test_agent_communication.py
```

## 🔧 Configuration

### Google Cloud Pub/Sub Setup
The system automatically creates the following topics and subscriptions:
- `ops-mesh-frontdesk_agent` - FrontDesk Agent messages
- `ops-mesh-queue_agent` - Queue Agent messages
- `ops-mesh-appointment_agent` - Appointment Agent messages
- `ops-mesh-notification_agent` - Notification Agent messages
- `ops-mesh-orchestrator_agent` - Orchestrator Agent messages

### Agent Configuration
Each agent can be configured through environment variables:
```bash
# Agent-specific settings
AGENT_LOG_LEVEL=INFO
AGENT_MAX_MESSAGES=10
AGENT_TIMEOUT=30
```

## 📋 Workflow Examples

### Patient Registration Workflow
1. **FrontDesk Agent** receives patient registration request
2. **FrontDesk Agent** registers patient and notifies **Queue Agent**
3. **Queue Agent** adds patient to queue and notifies **Notification Agent**
4. **Notification Agent** sends confirmation to patient

### Appointment Scheduling Workflow
1. **Appointment Agent** receives scheduling request
2. **Appointment Agent** schedules appointment and notifies **Notification Agent**
3. **Notification Agent** sends confirmation and reminder to patient

### Emergency Coordination Workflow
1. **Orchestrator Agent** receives emergency alert
2. **Orchestrator Agent** coordinates with all relevant agents
3. **Queue Agent** prioritizes emergency patient
4. **Notification Agent** sends urgent alerts to staff

## 🧪 Testing

### Unit Tests
```bash
# Run agent-specific tests
pytest tests/test_agents.py

# Run communication protocol tests
pytest tests/test_agent_protocol.py
```

### Integration Tests
```bash
# Test agent communication
python test_agent_communication.py

# Test specific workflows
python -m pytest tests/test_workflows.py
```

## 📊 Monitoring

### Logs
All agents log their activities to:
- Console output (INFO level)
- Google Cloud Logging (if configured)
- Local log files in `/tmp/agents_log/`

### Metrics
The system tracks:
- Message throughput
- Agent response times
- Workflow completion rates
- Error rates

### Health Checks
Each agent provides health status through:
```python
# Get agent status
status = await manager.get_agent_status()
```

## 🔒 Security

### Authentication
- Uses Google Cloud service account authentication
- Pub/Sub topics are project-scoped
- Message encryption in transit

### Authorization
- Agents can only access their designated topics
- Message validation and sanitization
- Rate limiting and throttling

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check service account
   gcloud auth application-default login
   ```

2. **Pub/Sub Permission Errors**
   ```bash
   # Grant Pub/Sub permissions
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:SERVICE_ACCOUNT" \
     --role="roles/pubsub.admin"
   ```

3. **Agent Connection Issues**
   ```bash
   # Check network connectivity
   ping pubsub.googleapis.com
   ```

### Debug Mode
```bash
# Enable debug logging
export AGENT_LOG_LEVEL=DEBUG
python start_agents.py
```

## 📈 Performance

### Optimization Tips
- Use message batching for high-volume scenarios
- Implement message caching for frequently accessed data
- Monitor Pub/Sub quotas and limits
- Use appropriate message priorities

### Scaling
- Agents can be horizontally scaled
- Pub/Sub automatically handles load balancing
- Consider regional deployment for latency

## 🔮 Future Enhancements

- **Machine Learning Integration**: AI-powered queue optimization
- **Real-time Analytics**: Live dashboard for agent performance
- **Multi-region Support**: Cross-region agent communication
- **Advanced Workflows**: Complex multi-agent coordination
- **Voice Integration**: Voice-based agent interactions

## 📚 API Reference

### Agent Protocol
```python
from app.agents.protocol import AgentProtocol, MessageType, Priority

# Create protocol instance
protocol = AgentProtocol("agent_id", "project_id")

# Send message
await protocol.send_message(
    recipient_id="target_agent",
    message_type=MessageType.REQUEST,
    payload={"action": "test"},
    priority=Priority.MEDIUM
)
```

### Agent Manager
```python
from app.agents.agent_manager import AgentManager

# Create manager
manager = AgentManager("project_id")

# Initialize and start all agents
await manager.initialize_all_agents()
await manager.start_all_agents()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
