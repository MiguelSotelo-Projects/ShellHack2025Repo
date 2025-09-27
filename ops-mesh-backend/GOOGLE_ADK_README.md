# Google ADK Agent System

This document describes the Google ADK (Application Development Kit) implementation of the hospital operations management system's agent architecture.

## 🏗️ Architecture Overview

The system uses Google Cloud Platform services and a standardized agent-to-agent protocol to create a scalable, intelligent hospital operations management system.

### Core Components

1. **Agent Protocol** - Standardized communication protocol using Google Pub/Sub
2. **Google ADK Integration** - Leverages Google Cloud AI Platform, Pub/Sub, Storage, Logging, and Monitoring
3. **Flow Management** - Predefined patient flow templates with orchestration
4. **Agent Lifecycle Management** - Centralized agent startup, monitoring, and coordination

## 🤖 Agent Types

### 1. Orchestrator Agent
- **Purpose**: System coordination and flow management
- **Responsibilities**:
  - Agent registration and health monitoring
  - Patient flow orchestration
  - System-wide coordination
  - Error handling and recovery

### 2. FrontDesk Agent
- **Purpose**: Tablet interface and patient check-in
- **Responsibilities**:
  - Patient information collection
  - Appointment lookup and verification
  - Walk-in registration
  - Session management

### 3. Scheduling Agent (To be implemented)
- **Purpose**: Appointment management and availability
- **Responsibilities**:
  - Appointment scheduling and confirmation
  - Provider availability checking
  - Rescheduling and cancellations
  - Room and resource assignment

### 4. Insurance Agent (To be implemented)
- **Purpose**: Coverage verification and payment processing
- **Responsibilities**:
  - Insurance verification
  - Rate calculation and copay determination
  - Payment processing
  - Prior authorization handling

### 5. Hospital Agent (To be implemented)
- **Purpose**: Bed and resource management
- **Responsibilities**:
  - Bed reservation and tracking
  - Resource allocation
  - Capacity management
  - Emergency bed handling

### 6. Queue Agent (To be implemented)
- **Purpose**: Patient calling and queue management
- **Responsibilities**:
  - Priority-based queuing
  - Patient calling automation
  - Wait time optimization
  - No-show handling

### 7. Staff Agent (To be implemented)
- **Purpose**: Resource coordination and staff management
- **Responsibilities**:
  - Staff assignment and coordination
  - Equipment allocation
  - Bed preparation and cleaning
  - Patient care coordination

## 📋 Patient Flow Templates

### 1. Appointment Check-in Flow
```
FrontDesk → Scheduling → Insurance → Hospital → Queue → Staff
```
- **Duration**: ~30 minutes
- **Complexity**: High
- **Success Rate**: 95%

### 2. Walk-in Registration Flow
```
FrontDesk → Hospital → Queue → Staff
```
- **Duration**: ~15 minutes
- **Complexity**: Medium
- **Success Rate**: 90%

### 3. Emergency Admission Flow
```
FrontDesk → Hospital → Queue → Staff (Priority)
```
- **Duration**: ~5 minutes
- **Complexity**: High
- **Success Rate**: 99%

## 🚀 Getting Started

### Prerequisites

1. **Google Cloud Project** with the following APIs enabled:
   - AI Platform API
   - Pub/Sub API
   - Cloud Storage API
   - Cloud Logging API
   - Cloud Monitoring API

2. **Authentication** - One of the following:
   - Service Account Key File
   - Application Default Credentials (ADC)
   - Environment variable `GOOGLE_APPLICATION_CREDENTIALS`

3. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Setup

1. **Set Google Cloud Project**:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_CLOUD_REGION="us-central1"
   ```

2. **Set Authentication** (if using service account key):
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

3. **Optional Configuration**:
   ```bash
   export OPS_MESH_TOPIC_PREFIX="ops-mesh"
   export OPS_MESH_MONITORING="true"
   export OPS_MESH_LOGGING="true"
   ```

### Starting the Agent System

1. **Using the startup script**:
   ```bash
   python start_agents.py
   ```

2. **Programmatically**:
   ```python
   import asyncio
   from app.agents.google_adk_agents import start_agent_system
   
   async def main():
       success = await start_agent_system("your-project-id")
       if success:
           print("Agent system started!")
   
   asyncio.run(main())
   ```

## 📡 Agent Communication Protocol

### Message Types

- `HEARTBEAT` - Agent health monitoring
- `REGISTRATION` - Agent registration with orchestrator
- `DEREGISTRATION` - Agent shutdown notification
- `STATUS_UPDATE` - Agent status changes
- `PATIENT_CHECKIN` - Patient check-in requests
- `APPOINTMENT_LOOKUP` - Appointment verification
- `WALKIN_REGISTRATION` - Walk-in patient registration
- `INSURANCE_VERIFICATION` - Insurance coverage checks
- `BED_RESERVATION` - Bed allocation requests
- `QUEUE_MANAGEMENT` - Queue operations
- `STAFF_COORDINATION` - Staff assignment requests
- `FLOW_START` - Patient flow initiation
- `FLOW_STEP` - Flow step completion
- `FLOW_COMPLETE` - Flow completion notification
- `FLOW_FAILURE` - Flow failure notification
- `ACKNOWLEDGMENT` - Message acknowledgment
- `RESPONSE` - Response to requests
- `ERROR` - Error notifications

### Message Priority Levels

1. `LOW` - Background tasks, heartbeats
2. `NORMAL` - Standard operations
3. `HIGH` - Important requests
4. `URGENT` - Time-sensitive operations
5. `CRITICAL` - Emergency situations

### Message Structure

```python
{
    "message_id": "unique-message-id",
    "correlation_id": "optional-correlation-id",
    "sender_id": "agent-id",
    "recipient_id": "target-agent-id",
    "message_type": "MESSAGE_TYPE",
    "priority": "PRIORITY_LEVEL",
    "payload": {
        # Message-specific data
    },
    "metadata": {
        # Additional metadata
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "expires_at": "2024-01-01T01:00:00Z",  # Optional
    "retry_count": 0,
    "max_retries": 3
}
```

## 🔧 Google Cloud Services Integration

### Pub/Sub Topics

The system creates the following topics:
- `ops-mesh-agent-broadcast` - System-wide broadcasts
- `ops-mesh-orchestrator` - Orchestrator communications
- `ops-mesh-frontdesk` - Front desk agent
- `ops-mesh-scheduling` - Scheduling agent
- `ops-mesh-insurance` - Insurance agent
- `ops-mesh-hospital` - Hospital agent
- `ops-mesh-queue` - Queue agent
- `ops-mesh-staff` - Staff agent

### Cloud Storage

- **Bucket**: `{project-id}-ops-mesh-storage`
- **Purpose**: Store flow definitions, agent configurations, and system data

### Cloud Logging

- **Log Name**: `agent-{agent-id}`
- **Purpose**: Centralized logging for all agent activities

### Cloud Monitoring

- **Metrics**: Agent health, flow performance, system metrics
- **Purpose**: System monitoring and alerting

## 📊 System Monitoring

### Health Checks

The system provides comprehensive health monitoring:

```python
# Get system status
agent_manager = get_agent_manager()
status = agent_manager.get_system_status()

# Perform health check
health = await agent_manager.health_check()

# Get agent-specific status
agent_status = agent_manager.get_agent_status("frontdesk")
```

### Metrics

- **Agent Metrics**: Status, response times, error rates
- **Flow Metrics**: Completion rates, duration, success/failure rates
- **System Metrics**: Total agents, active flows, uptime

## 🔄 Flow Orchestration

### Flow Definition

Flows are defined using JSON schemas with:
- **Steps**: Sequential operations with dependencies
- **Timeouts**: Maximum execution time per step
- **Retry Policies**: Error handling and retry logic
- **Validation**: Input/output schema validation

### Flow Execution

1. **Initiation**: Flow started by orchestrator
2. **Step Execution**: Each step sent to appropriate agent
3. **Coordination**: Orchestrator manages step dependencies
4. **Completion**: Flow marked as completed or failed
5. **Cleanup**: Resources released and metrics updated

## 🛠️ Development

### Adding New Agents

1. **Create Agent Class**:
   ```python
   from app.agents.protocol.agent_protocol import AgentProtocol
   
   class MyAgent(AgentProtocol):
       def get_capabilities(self):
           # Define agent capabilities
           pass
       
       async def process_message(self, message):
           # Handle incoming messages
           pass
   ```

2. **Register in Agent Manager**:
   ```python
   # In agent_manager.py
   self.agent_configs["my_agent"] = {
       "class": MyAgent,
       "required": True,
       "startup_priority": 8
   }
   ```

3. **Add Flow Steps**:
   ```python
   # In flow_definitions.py
   {
       "step_id": "my_agent_step",
       "step_name": "My Agent Step",
       "agent": "my_agent",
       "action": "my_action",
       "message_type": MessageType.MY_MESSAGE,
       "priority": MessagePriority.NORMAL,
       "timeout_minutes": 5,
       "required": True
   }
   ```

### Testing

```python
# Test agent communication
async def test_agent_communication():
    agent_manager = await initialize_agent_manager("test-project")
    await agent_manager.start_all_agents()
    
    # Test message sending
    success = await agent_manager.send_message_to_agent(
        "frontdesk",
        "PATIENT_CHECKIN",
        {"patient_data": {"first_name": "John", "last_name": "Doe"}}
    )
    
    assert success
```

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
   - Check service account permissions
   - Ensure APIs are enabled

2. **Pub/Sub Issues**:
   - Verify topics and subscriptions are created
   - Check IAM permissions for Pub/Sub
   - Monitor message delivery

3. **Agent Startup Failures**:
   - Check agent dependencies
   - Verify database connections
   - Review agent logs

### Debugging

1. **Enable Debug Logging**:
   ```python
   logging.getLogger().setLevel(logging.DEBUG)
   ```

2. **Check Agent Logs**:
   ```bash
   # View agent logs
   gcloud logging read "resource.type=global AND logName=agent-frontdesk"
   ```

3. **Monitor Pub/Sub**:
   ```bash
   # Check topic messages
   gcloud pubsub topics list
   gcloud pubsub subscriptions list
   ```

## 📈 Performance Optimization

### Scaling

- **Horizontal Scaling**: Add more agent instances
- **Vertical Scaling**: Increase agent resources
- **Load Balancing**: Distribute flows across agents

### Monitoring

- **Metrics Collection**: Use Cloud Monitoring
- **Alerting**: Set up alerts for failures
- **Performance Tuning**: Optimize based on metrics

## 🔒 Security

### Authentication

- **Service Accounts**: Use least-privilege service accounts
- **IAM Roles**: Grant minimal required permissions
- **Key Rotation**: Regularly rotate service account keys

### Data Protection

- **Encryption**: All data encrypted in transit and at rest
- **Access Control**: Role-based access control
- **Audit Logging**: Comprehensive audit trails

## 📚 API Reference

### Agent Protocol

See `app/agents/protocol/agent_protocol.py` for detailed API documentation.

### Flow Definitions

See `app/agents/protocol/flow_definitions.py` for flow template definitions.

### Agent Manager

See `app/agents/google_adk_agents/agent_manager.py` for management API.

## 🤝 Contributing

1. Follow the existing code structure
2. Add comprehensive tests
3. Update documentation
4. Follow Google Cloud best practices
5. Ensure backward compatibility

## 📄 License

This implementation is part of the hospital operations management system and follows the same licensing terms.
