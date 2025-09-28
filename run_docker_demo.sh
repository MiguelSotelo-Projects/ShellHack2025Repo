#!/bin/bash

# ShellHacks 2025 - Docker Demo Runner
# This script builds and runs the entire demo using Docker

set -e

echo "🐳 ShellHacks 2025 - Docker Demo Runner"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker and Docker Compose are available"

# Check if ports are available
print_status "Checking port availability..."
if lsof -ti:8000,3000 &> /dev/null; then
    print_warning "Ports 8000 and/or 3000 are already in use"
    print_status "Stopping existing processes..."
    
    # Kill processes on ports 8000 and 3000
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    sleep 2
    print_success "Ports freed"
fi

# Create data directory if it doesn't exist
mkdir -p ./data

# Build and start the demo
print_status "Building Docker image..."
docker-compose build --no-cache

print_status "Starting the demo..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Check if services are running
print_status "Checking service health..."

# Check backend
for i in {1..30}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start"
        docker-compose logs
        exit 1
    fi
    sleep 2
done

# Check frontend
for i in {1..30}; do
    if curl -f http://localhost:3000 &> /dev/null; then
        print_success "Frontend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Frontend failed to start"
        docker-compose logs
        exit 1
    fi
    sleep 2
done

echo ""
echo "🎊 Demo is running successfully in Docker!"
echo "=========================================="
echo "🌐 Available URLs:"
echo "   • Main Dashboard: http://localhost:3000"
echo "   • Enhanced Dashboard: http://localhost:3000/enhanced-dashboard"
echo "   • Agent Demo: http://localhost:3000/agent-demo"
echo "   • Live Dashboard: http://localhost:3000/live-dashboard"
echo "   • Patient Flow: http://localhost:3000/patient-flow"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo ""
echo "🐳 Docker Commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop demo: docker-compose down"
echo "   • Restart: docker-compose restart"
echo "   • Shell access: docker-compose exec ops-mesh-demo bash"
echo ""
echo "✨ Features Available:"
echo "   • Visual agent status monitoring"
echo "   • Patient management with status updates"
echo "   • Queue management with dequeue operations"
echo "   • Real-time statistics and activity logs"
echo "   • A2A protocol workflow testing"
echo "   • Agent-to-agent communication"
echo ""
echo "🛑 To stop the demo, run: docker-compose down"
echo "=========================================="
