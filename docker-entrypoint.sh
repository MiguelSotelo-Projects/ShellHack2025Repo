#!/bin/bash

# ShellHacks 2025 - Docker Entrypoint Script
# This script starts both the backend and frontend services

set -e

echo "🎉 Starting ShellHacks 2025 Ops Mesh Demo in Docker"
echo "=================================================="

# Function to handle cleanup
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Create database directory if it doesn't exist
mkdir -p /app/data

# Initialize database
echo "🔧 Setting up database..."
cd /app
python -c "
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database initialized successfully')
"

# Start backend server
echo "🚀 Starting backend server..."
cd /app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        exit 1
    fi
    sleep 1
done

# Start frontend server
echo "🎨 Starting frontend server..."
cd /app/frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to start..."
for i in {1..30}; do
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start"
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎊 Demo is running successfully!"
echo "=================================================="
echo "🌐 Available URLs:"
echo "   • Main Dashboard: http://localhost:3000"
echo "   • Enhanced Dashboard: http://localhost:3000/enhanced-dashboard"
echo "   • Agent Demo: http://localhost:3000/agent-demo"
echo "   • Live Dashboard: http://localhost:3000/live-dashboard"
echo "   • Patient Flow: http://localhost:3000/patient-flow"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo ""
echo "✨ Features Available:"
echo "   • Visual agent status monitoring"
echo "   • Patient management with status updates"
echo "   • Queue management with dequeue operations"
echo "   • Real-time statistics and activity logs"
echo "   • A2A protocol workflow testing"
echo "   • Agent-to-agent communication"
echo ""
echo "🛑 Press Ctrl+C to stop the demo"
echo "=================================================="

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
