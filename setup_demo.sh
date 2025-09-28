#!/bin/bash

# ShellHacks 2025 - Enhanced Demo Setup Script
echo "🎉 Setting up Enhanced Ops Mesh Demo..."

# Check if we're in the right directory
if [ ! -f "start_demo.py" ]; then
    echo "❌ Please run this script from the ShellHack2025Repo root directory"
    exit 1
fi

echo "📦 Installing backend dependencies..."
cd ops-mesh-backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create database
echo "Creating database..."
python -c "
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database created successfully')
"

cd ..

echo "📦 Installing frontend dependencies..."
cd ops-mesh-frontend

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

cd ..

echo "🎯 Demo setup complete!"
echo ""
echo "🚀 To start the enhanced demo:"
echo "   python start_demo.py"
echo ""
echo "🌐 Available URLs:"
echo "   • Main Dashboard: http://localhost:3000"
echo "   • Enhanced Dashboard: http://localhost:3000/enhanced-dashboard"
echo "   • Agent Demo: http://localhost:3000/agent-demo"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "✨ Features available:"
echo "   • Visual agent status monitoring"
echo "   • Patient management with status updates"
echo "   • Queue management with dequeue operations"
echo "   • Real-time statistics and activity logs"
echo "   • A2A protocol workflow testing"
echo ""
echo "🎊 Ready for your ShellHacks presentation!"
