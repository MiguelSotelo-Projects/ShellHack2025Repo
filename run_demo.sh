#!/bin/bash

# ShellHacks 2025 - Unix/Linux/macOS Demo Runner
# This is a simple wrapper for Unix-like systems

echo "🎉 ShellHacks 2025 - Ops Mesh Demo"
echo "===================================="

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if the Python script exists
if [ ! -f "run_full_demo.py" ]; then
    echo "❌ run_full_demo.py not found"
    echo "Please make sure you're in the correct directory"
    exit 1
fi

# Make the script executable
chmod +x run_full_demo.py

# Run the main Python script
echo "🚀 Starting the demo..."
python3 run_full_demo.py 2>/dev/null || python run_full_demo.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Demo failed to start"
    exit 1
fi
