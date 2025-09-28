# Ops Mesh Backend

A comprehensive hospital operations management system with intelligent agent-based automation using Google ADK (Application Development Kit).

## 🏥 Overview

Ops Mesh Backend is a modern hospital operations management system that uses intelligent agents to automate patient flow, appointment scheduling, bed management, and resource coordination. The system leverages Google Cloud Platform services for scalability, reliability, and intelligent automation.

## 🚀 Features

### Core Functionality
- **Patient Management**: Complete patient registration and information management
- **Appointment Scheduling**: Intelligent appointment booking and management
- **Queue Management**: Priority-based patient queuing and calling
- **Bed Management**: Real-time bed reservation and allocation
- **Walk-in Registration**: Streamlined walk-in patient processing
- **Dashboard Analytics**: Real-time operational insights and KPIs

### Intelligent Agent System (A2A Protocol)
- **FrontDesk Agent**: Patient registration and check-in automation
- **Queue Agent**: Patient calling and queue optimization
- **Appointment Agent**: Appointment management and scheduling
- **Notification Agent**: Alerts and notifications management
- **Orchestrator Agent**: System-wide coordination and workflow management

### Technology Stack
- **Backend**: FastAPI with Python 3.8+
- **Database**: SQLAlchemy with SQLite (production-ready for PostgreSQL)
- **Agent System**: Google ADK with A2A (Agent-to-Agent) protocol
- **Cloud Services**: Google Cloud Platform (AI Platform, Pub/Sub, Storage, Logging, Monitoring)
- **Real-time**: WebSocket support for live updates
- **Testing**: Comprehensive test suite with pytest
- **A2A Protocol**: Official Agent-to-Agent communication protocol

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Agent System  │
│   (Tablet/Web)  │◄──►│   (FastAPI)     │◄──►│   (Google ADK)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLAlchemy)  │
                       └─────────────────┘
```

### Agent Communication Flow

```
Patient Check-in → FrontDesk Agent → Orchestrator Agent
                                        │
                                        ▼
                    ┌─────────────────────────────────┐
                    │        Flow Orchestration       │
                    └─────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            Scheduling Agent    Insurance Agent    Hospital Agent
                    │                   │                   │
                    ▼                   ▼                   ▼
            Queue Agent ←───────────────┼───────────────────┘
                    │
                    ▼
            Staff Agent
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Google Cloud Project** with billing enabled
3. **Google Cloud CLI** installed and configured

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ops-mesh-backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up A2A configuration**:
   ```bash
   # Automated A2A setup (recommended)
   python setup_a2a.py --setup
   
   # Or manual setup (see A2A_IMPLEMENTATION_README.md)
   ```

4. **Test the A2A implementation**:
   ```bash
   python test_a2a_implementation.py
   ```

5. **Start the system**:
   ```bash
   # Start the A2A server with all agents
   python setup_a2a.py --start
   
   # Or start the API server
   python run.py
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Ops Mesh Configuration
OPS_MESH_TOPIC_PREFIX=ops-mesh
OPS_MESH_MONITORING=true
OPS_MESH_LOGGING=true

# Database Configuration
DATABASE_URL=sqlite:///./ops_mesh.db

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Ops Mesh Backend

# Development Settings
DEBUG=true
RELOAD=true
```

### A2A Protocol Setup

The system uses the A2A (Agent-to-Agent) protocol for agent communication:

- **Agent Discovery**: Automatic agent discovery and capability management
- **Task Coordination**: Structured task-based communication
- **Workflow Orchestration**: Multi-agent workflow management
- **Health Monitoring**: Agent health and status monitoring

### Google Cloud Setup

The system requires the following Google Cloud services:

- **AI Platform API**: For intelligent agent capabilities
- **Pub/Sub API**: For agent-to-agent communication (legacy)
- **Cloud Storage API**: For data storage and flow definitions
- **Cloud Logging API**: For centralized logging
- **Cloud Monitoring API**: For system monitoring

Required IAM roles for the service account:
- `roles/aiplatform.user`
- `roles/pubsub.admin`
- `roles/storage.admin`
- `roles/logging.logWriter`
- `roles/monitoring.metricWriter`
- `roles/monitoring.viewer`

## 📡 API Endpoints

### Core APIs

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`

### Patient Management
- `GET /api/v1/patients` - List patients
- `POST /api/v1/patients` - Create patient
- `GET /api/v1/patients/{id}` - Get patient
- `PUT /api/v1/patients/{id}` - Update patient
- `DELETE /api/v1/patients/{id}` - Delete patient

### Appointment Management
- `GET /api/v1/appointments` - List appointments
- `POST /api/v1/appointments` - Create appointment
- `GET /api/v1/appointments/{id}` - Get appointment
- `PUT /api/v1/appointments/{id}` - Update appointment
- `DELETE /api/v1/appointments/{id}` - Delete appointment
- `POST /api/v1/appointments/{id}/checkin` - Check in appointment
- `POST /api/v1/appointments/{id}/cancel` - Cancel appointment

### Queue Management
- `GET /api/v1/queue` - Get queue status
- `POST /api/v1/queue` - Add to queue
- `PUT /api/v1/queue/{id}` - Update queue item
- `DELETE /api/v1/queue/{id}` - Remove from queue

### Walk-in Management
- `POST /api/v1/walkin` - Register walk-in patient

### Check-in Management
- `POST /api/v1/checkin` - Process check-in

### Dashboard
- `GET /api/v1/dashboard/stats` - Get system statistics
- `GET /api/v1/dashboard/queue-summary` - Get queue summary
- `GET /api/v1/dashboard/kpis` - Get KPIs

## 🤖 A2A Agent System

### Agent Types

1. **FrontDesk Agent**: Handles patient registration and check-in
2. **Queue Agent**: Manages patient queues and wait times
3. **Appointment Agent**: Manages appointment scheduling and coordination
4. **Notification Agent**: Sends notifications and alerts
5. **Orchestrator Agent**: Coordinates complex workflows between agents

### A2A Protocol Features

- **Agent Discovery**: Automatic discovery of available agents and capabilities
- **Task-Based Communication**: Structured task requests and responses
- **Workflow Orchestration**: Multi-step workflow coordination
- **Health Monitoring**: Real-time agent health and status monitoring
- **Capability Management**: Dynamic capability discovery and matching

### Patient Flows

#### Appointment Check-in Flow (A2A)
```
FrontDesk Agent → Queue Agent → Notification Agent
Duration: ~30 minutes | Success Rate: 95%
```

#### Walk-in Registration Flow (A2A)
```
FrontDesk Agent → Queue Agent → Notification Agent
Duration: ~15 minutes | Success Rate: 90%
```

#### Emergency Admission Flow (A2A)
```
FrontDesk Agent → Queue Agent (Priority) → Notification Agent (Alert)
Duration: ~5 minutes | Success Rate: 99%
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run A2A implementation tests
python test_a2a_implementation.py

# Run with coverage
pytest --cov=app

# Run specific test categories
pytest tests/test_agents.py
pytest tests/test_appointments.py
pytest tests/test_queue.py
pytest tests/test_walkin.py
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **A2A Tests**: A2A protocol and agent communication testing
- **Agent Tests**: Agent functionality testing
- **Flow Tests**: Patient flow testing
- **Discovery Tests**: Agent discovery and capability testing

## 📊 Monitoring

### System Metrics

- **Agent Health**: Real-time agent status monitoring via A2A protocol
- **Flow Performance**: Patient flow completion rates and timing
- **Queue Metrics**: Wait times and queue optimization
- **Resource Utilization**: Bed and staff utilization rates
- **A2A Protocol Metrics**: Task completion rates and communication performance
- **Discovery Service Metrics**: Agent registration and capability discovery stats

### Google Cloud Monitoring

The system integrates with Google Cloud Monitoring for:
- **Custom Metrics**: Agent performance and flow metrics
- **Logging**: Centralized logging with Cloud Logging
- **Alerting**: Automated alerts for system issues
- **Dashboards**: Real-time operational dashboards

## 🔒 Security

### Authentication & Authorization

- **Service Account**: Google Cloud service account authentication
- **IAM Roles**: Role-based access control
- **API Security**: FastAPI security features
- **Data Encryption**: All data encrypted in transit and at rest

### Best Practices

- **Least Privilege**: Minimal required permissions
- **Key Rotation**: Regular service account key rotation
- **Audit Logging**: Comprehensive audit trails
- **Network Security**: VPC and firewall configuration

## 📈 Performance

### Scalability

- **Horizontal Scaling**: Add more agent instances
- **Vertical Scaling**: Increase agent resources
- **Load Balancing**: Distribute flows across agents
- **Auto-scaling**: Google Cloud auto-scaling capabilities

### Optimization

- **Message Batching**: Efficient Pub/Sub message handling
- **Caching**: Intelligent caching strategies
- **Database Optimization**: Query optimization and indexing
- **Resource Management**: Efficient resource allocation

## 🛠️ Development

### Project Structure

```
ops-mesh-backend/
├── app/
│   ├── agents/                 # Agent implementations
│   │   ├── protocol/          # Agent protocol and Google ADK
│   │   ├── google_adk_agents/ # Google ADK agent implementations
│   │   └── ...               # Other agent implementations
│   ├── api/                   # API endpoints
│   ├── core/                  # Core configuration
│   ├── models/                # Database models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic services
│   └── websockets/            # WebSocket handlers
├── tests/                     # Test suite
├── migrations/                # Database migrations
├── scripts/                   # Utility scripts
└── docs/                      # Documentation
```

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

## 📚 Documentation

- **[A2A Implementation Guide](A2A_IMPLEMENTATION_README.md)**: Complete A2A setup and implementation guide
- **[Agent Communication README](AGENT_COMMUNICATION_README.md)**: Agent-to-agent communication system
- **[API Documentation](http://localhost:8000/docs)**: Interactive API documentation
- **[A2A Protocol](app/agents/protocol/a2a_protocol.py)**: A2A protocol implementation
- **[Agent Discovery](app/agents/discovery_service.py)**: Agent discovery service

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Update documentation**
6. **Submit a pull request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive tests including A2A protocol tests
- Update documentation and agent cards
- Follow Google ADK and A2A protocol best practices
- Ensure backward compatibility
- Update agent capabilities when adding new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help

1. **Check the documentation**: Review A2A implementation guide and API docs
2. **Run tests**: Use `python test_a2a_implementation.py` to diagnose issues
3. **Check logs**: Review agent system and A2A protocol logs
4. **Google Cloud Console**: Check for errors in the console
5. **Community Support**: Use GitHub issues for questions

### Common Issues

- **Authentication Errors**: Verify service account configuration
- **API Not Enabled**: Enable required Google Cloud APIs
- **Permission Issues**: Check IAM roles and permissions
- **Network Issues**: Verify firewall and VPC configuration
- **A2A Protocol Issues**: Check agent cards and discovery service
- **Agent Registration Issues**: Verify agent capabilities and dependencies

## 🎯 Roadmap

### Upcoming Features

- **Advanced A2A Features**: Enhanced workflow orchestration and agent learning
- **Machine Learning**: AI-powered patient flow optimization
- **Mobile App**: Native mobile application with A2A integration
- **Advanced Analytics**: Predictive analytics and insights
- **Integration**: Third-party system integrations via A2A protocol
- **Multi-tenant**: Support for multiple hospitals with A2A coordination

### Performance Improvements

- **A2A Optimization**: Enhanced task batching and agent pooling
- **Caching Layer**: Redis caching implementation
- **Database Optimization**: PostgreSQL migration
- **Real-time Updates**: WebSocket enhancements with A2A integration
- **Load Balancing**: Advanced load balancing strategies for agents

---

**Built with ❤️ for better healthcare operations**
