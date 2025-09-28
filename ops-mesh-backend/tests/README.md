# Testing Guide for Ops Mesh Backend

This directory contains comprehensive unit tests for the Ops Mesh Backend application.

## Test Structure

```
tests/
├── conftest.py              # Test fixtures and configuration
├── test_core_config.py      # Tests for configuration management
├── test_core_database.py    # Tests for database setup and utilities
├── test_core_redis.py       # Tests for Redis configuration (placeholder)
├── test_models_patient.py   # Tests for Patient model
├── test_models_appointment.py # Tests for Appointment model
├── test_appointments.py     # Tests for appointment API endpoints
├── test_queue.py           # Tests for queue API endpoints
├── test_walkin.py          # Tests for walk-in API endpoints
├── test_main.py            # Tests for main FastAPI application
├── test_utils_common.py    # Tests for common utility functions
├── test_services.py        # Tests for service layer (placeholder)
├── test_agents.py          # Tests for agent system (placeholder)
└── README.md               # This file
```

## Test Categories

### 1. Core Tests
- **Configuration Tests**: Test application settings and environment variable handling
- **Database Tests**: Test database connection, session management, and utilities
- **Redis Tests**: Test Redis configuration (placeholder for future implementation)

### 2. Model Tests
- **Patient Model**: Test patient data model, validation, and relationships
- **Appointment Model**: Test appointment data model, status transitions, and relationships
- **Queue Model**: Test queue entry model and status management

### 3. API Tests
- **Appointment API**: Test all appointment-related endpoints
- **Queue API**: Test queue management endpoints
- **Walk-in API**: Test walk-in patient handling endpoints
- **Main App**: Test application setup, routing, and middleware

### 4. Utility Tests
- **Common Utils**: Test utility functions like code generation and timestamps

### 5. Service Tests (Placeholder)
- **Appointment Service**: Test business logic for appointments
- **Dashboard Service**: Test dashboard data aggregation
- **Queue Service**: Test queue management logic
- **Walk-in Service**: Test walk-in patient processing
- **Notification Service**: Test notification handling

### 6. Agent Tests (Placeholder)
- **Base Agent**: Test agent base class functionality
- **Appointment Agent**: Test appointment scheduling agent
- **Intake Agent**: Test patient intake agent
- **Orchestrator Agent**: Test agent coordination
- **A2A Communication**: Test agent-to-agent communication

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

### Basic Test Execution

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_appointments.py
```

Run specific test function:
```bash
pytest tests/test_appointments.py::TestAppointmentAPI::test_create_appointment
```

### Using the Test Runner Script

The project includes a custom test runner script with additional features:

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run only unit tests
python run_tests.py --category unit

# Run only API tests
python run_tests.py --category api

# Skip slow tests
python run_tests.py --fast

# Install dependencies and run tests
python run_tests.py --install-deps --coverage
```

### Test Categories

Run tests by category using markers:
```bash
# Unit tests only
pytest -m unit

# API tests only
pytest -m api

# Model tests only
pytest -m model

# Skip slow tests
pytest -m "not slow"
```

### Coverage Reports

Generate coverage reports:
```bash
# Terminal coverage report
pytest --cov=app --cov-report=term

# HTML coverage report
pytest --cov=app --cov-report=html

# Both terminal and HTML
pytest --cov=app --cov-report=term --cov-report=html
```

View HTML coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

### Database Fixtures
- `db_session`: Fresh database session for each test
- `client`: FastAPI test client with database override

### Data Fixtures
- `sample_patient_data`: Generated patient data
- `sample_patient`: Patient instance in database
- `sample_appointment_data`: Generated appointment data
- `sample_appointment`: Appointment instance in database
- `multiple_patients`: Multiple patient instances
- `multiple_appointments`: Multiple appointment instances

### Usage Example
```python
def test_something(client, sample_patient, db_session):
    # Use the test client and fixtures
    response = client.get(f"/api/v1/patients/{sample_patient.id}")
    assert response.status_code == 200
```

## Test Database

Tests use a separate SQLite test database (`test.db`) that is:
- Created fresh for each test session
- Rolled back after each test
- Isolated from the main application database

## Writing New Tests

### Test File Structure
```python
import pytest
from fastapi.testclient import TestClient

class TestNewFeature:
    """Test cases for new feature."""
    
    def test_basic_functionality(self, client):
        """Test basic functionality."""
        response = client.get("/api/v1/new-feature/")
        assert response.status_code == 200
    
    def test_with_fixtures(self, client, sample_patient):
        """Test using fixtures."""
        # Test implementation
        pass
```

### Test Naming Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names that explain what is being tested

### Assertions
Use specific assertions:
```python
# Good
assert response.status_code == 200
assert "expected_field" in response.json()
assert response.json()["status"] == "success"

# Avoid
assert response  # Too generic
```

### Test Data
- Use the provided fixtures when possible
- Generate test data using Faker for realistic data
- Clean up test data in fixtures (handled automatically)

## Continuous Integration

The test suite is designed to run in CI environments:
- No external dependencies required
- Fast execution (most tests complete in seconds)
- Clear error messages and reporting
- Coverage reporting for code quality

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running tests from the project root directory
2. **Database Errors**: Ensure test database permissions are correct
3. **Fixture Errors**: Check that fixtures are properly defined in `conftest.py`

### Debug Mode
Run tests with debug output:
```bash
pytest -vvv --tb=long
```

### Test Discovery
Check which tests will be run:
```bash
pytest --collect-only
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve test coverage
4. Update this README if adding new test categories

## Test Coverage Goals

- **Core modules**: 100% coverage
- **API endpoints**: 95%+ coverage
- **Models**: 100% coverage
- **Utilities**: 100% coverage
- **Services**: 90%+ coverage (when implemented)
- **Agents**: 90%+ coverage (when implemented)

Current coverage can be checked by running:
```bash
python run_tests.py --coverage
```
