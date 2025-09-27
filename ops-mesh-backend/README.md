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

### Intelligent Agent System
- **FrontDesk Agent**: Tablet interface and patient check-in automation
- **Scheduling Agent**: Appointment management and availability optimization
- **Insurance Agent**: Coverage verification and payment processing
- **Hospital Agent**: Bed and resource management
- **Queue Agent**: Patient calling and queue optimization
- **Staff Agent**: Resource coordination and staff management
- **Orchestrator Agent**: System-wide coordination and flow management

### Technology Stack
- **Backend**: FastAPI with Python 3.8+
- **Database**: SQLAlchemy with SQLite (production-ready for PostgreSQL)
- **Agent System**: Google ADK with Pub/Sub messaging
- **Cloud Services**: Google Cloud Platform (AI Platform, Pub/Sub, Storage, Logging, Monitoring)
- **Real-time**: WebSocket support for live updates
- **Testing**: Comprehensive test suite with pytest

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

3. **Set up Google Cloud configuration**:
   ```bash
   # Automated setup (recommended)
   python setup_google_adk.py
   
   # Or manual setup (see GOOGLE_ADK_SETUP.md)
   ```

4. **Test the configuration**:
   ```bash
   python test_google_adk.py
   ```

5. **Start the system**:
   ```bash
   # Start the agent system
   python start_agents.py
   
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

### Google Cloud Setup

The system requires the following Google Cloud services:

- **AI Platform API**: For intelligent agent capabilities
- **Pub/Sub API**: For agent-to-agent communication
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

## 🤖 Agent System

### Agent Types

1. **FrontDesk Agent**: Handles tablet interface and patient check-in
2. **Scheduling Agent**: Manages appointments and availability
3. **Insurance Agent**: Processes coverage verification and payments
4. **Hospital Agent**: Manages bed reservations and resources
5. **Queue Agent**: Handles patient calling and queue optimization
6. **Staff Agent**: Coordinates staff assignments and resources
7. **Orchestrator Agent**: Coordinates system-wide operations

### Patient Flows

#### Appointment Check-in Flow
```
FrontDesk → Scheduling → Insurance → Hospital → Queue → Staff
Duration: ~30 minutes | Success Rate: 95%
```

#### Walk-in Registration Flow
```
FrontDesk → Hospital → Queue → Staff
Duration: ~15 minutes | Success Rate: 90%
```

#### Emergency Admission Flow
```
FrontDesk → Hospital → Queue → Staff (Priority)
Duration: ~5 minutes | Success Rate: 99%
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

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
- **Agent Tests**: Agent communication testing
- **Flow Tests**: Patient flow testing

## 📊 Monitoring

### System Metrics

- **Agent Health**: Real-time agent status monitoring
- **Flow Performance**: Patient flow completion rates and timing
- **Queue Metrics**: Wait times and queue optimization
- **Resource Utilization**: Bed and staff utilization rates

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

- **[Google ADK Setup Guide](GOOGLE_ADK_SETUP.md)**: Complete setup instructions
- **[Google ADK Implementation](GOOGLE_ADK_README.md)**: Technical implementation details
- **[API Documentation](http://localhost:8000/docs)**: Interactive API documentation
- **[Agent Protocol](app/agents/protocol/)**: Agent communication protocol

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Update documentation**
6. **Submit a pull request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive tests
- Update documentation
- Follow Google Cloud best practices
- Ensure backward compatibility

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help

1. **Check the documentation**: Review setup guides and API docs
2. **Run tests**: Use `python test_google_adk.py` to diagnose issues
3. **Check logs**: Review agent system and API logs
4. **Google Cloud Console**: Check for errors in the console
5. **Community Support**: Use GitHub issues for questions

### Common Issues

- **Authentication Errors**: Verify service account configuration
- **API Not Enabled**: Enable required Google Cloud APIs
- **Permission Issues**: Check IAM roles and permissions
- **Network Issues**: Verify firewall and VPC configuration

## 🎯 Roadmap

### Upcoming Features

- **Machine Learning**: AI-powered patient flow optimization
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Predictive analytics and insights
- **Integration**: Third-party system integrations
- **Multi-tenant**: Support for multiple hospitals

### Performance Improvements

- **Caching Layer**: Redis caching implementation
- **Database Optimization**: PostgreSQL migration
- **Real-time Updates**: WebSocket enhancements
- **Load Balancing**: Advanced load balancing strategies

---

**Built with ❤️ for better healthcare operations**
