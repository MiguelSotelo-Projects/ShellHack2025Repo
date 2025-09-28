# 🚀 Complete Demo Runner - ShellHacks 2025

This repository now includes a comprehensive demo runner that handles the entire setup and execution process for the Ops Mesh A2A Protocol Demo.

## 🎯 Quick Start

### Option 1: One-Click Run (Recommended)

**Windows:**
```cmd
run_demo.bat
```

**macOS/Linux:**
```bash
./run_demo.sh
```

### Option 2: Python Script (Cross-Platform)

```bash
python run_full_demo.py
```

## 📋 What the Demo Runner Does

The `run_full_demo.py` script provides a complete solution that:

### ✅ **Automatic Setup**
- Checks system prerequisites (Python 3.8+, Node.js, npm)
- Verifies port availability (8000 for backend, 3000 for frontend)
- Creates Python virtual environment
- Installs all backend dependencies
- Installs all frontend dependencies
- Sets up the database with proper tables

### ✅ **Smart Process Management**
- Starts backend server with proper virtual environment
- Starts frontend development server
- Monitors both processes for health
- Handles graceful shutdown on Ctrl+C
- Cross-platform compatibility (Windows, macOS, Linux)

### ✅ **User-Friendly Interface**
- Colored terminal output for better readability
- Progress indicators and status messages
- Comprehensive error handling and reporting
- Clear instructions and helpful URLs

### ✅ **Robust Error Handling**
- Validates prerequisites before starting
- Checks for port conflicts
- Handles dependency installation failures
- Provides clear error messages and solutions

## 🛠️ Command Line Options

```bash
python run_full_demo.py [OPTIONS]

Options:
  --setup-only    Only run setup, don't start the demo
  --skip-setup    Skip setup and go directly to running the demo
  --help          Show help message
```

### Examples:

```bash
# Run complete setup and demo (default)
python run_full_demo.py

# Only run setup (useful for CI/CD)
python run_full_demo.py --setup-only

# Skip setup and run demo (if already set up)
python run_full_demo.py --skip-setup
```

## 🌐 Demo URLs

Once running, the demo provides access to:

- **🏠 Main Dashboard**: http://localhost:3000
- **✨ Enhanced Dashboard**: http://localhost:3000/enhanced-dashboard
- **🤖 Agent Demo**: http://localhost:3000/agent-demo
- **📊 Live Dashboard**: http://localhost:3000/live-dashboard
- **👥 Patient Flow**: http://localhost:3000/patient-flow
- **📚 API Documentation**: http://localhost:8000/docs
- **❤️ Health Check**: http://localhost:8000/health

## 🎮 Demo Features

### **Agent-to-Agent Communication**
- Real-time agent status monitoring
- A2A protocol workflow testing
- Agent discovery and capability management
- Multi-agent coordination

### **Patient Management**
- Patient registration and check-in
- Walk-in patient handling
- Appointment scheduling
- Queue management with priority handling

### **Real-time Monitoring**
- Live dashboard with statistics
- Queue status and wait times
- Agent activity logs
- Performance metrics

## 🔧 Technical Details

### **Backend (FastAPI)**
- Python 3.8+ with virtual environment
- SQLite database with SQLAlchemy ORM
- RESTful API with automatic documentation
- WebSocket support for real-time updates
- A2A protocol implementation

### **Frontend (Next.js)**
- React 19 with TypeScript
- Tailwind CSS for styling
- Real-time data updates
- Responsive design for multiple devices

### **Dependencies**
- **Backend**: FastAPI, SQLAlchemy, Pydantic, WebSockets
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Agent System**: Custom A2A protocol implementation

## 🚨 Troubleshooting

### **Common Issues**

#### Port Already in Use
```
❌ Port 8000 is already in use
```
**Solution**: Stop other services using ports 8000 or 3000, or modify the ports in the script.

#### Python Not Found
```
❌ Python 3 is not installed or not in PATH
```
**Solution**: Install Python 3.8+ and ensure it's in your system PATH.

#### Node.js Not Found
```
❌ Node.js/npm is not installed or not in PATH
```
**Solution**: Install Node.js (which includes npm) from https://nodejs.org/

#### Permission Denied (Unix/macOS)
```
❌ Permission denied
```
**Solution**: Make the script executable:
```bash
chmod +x run_demo.sh
chmod +x run_full_demo.py
```

### **Manual Setup (If Needed)**

If the automated setup fails, you can run the original setup script:

```bash
# Unix/macOS
./setup_demo.sh

# Then start manually
python start_demo.py
```

## 🎊 Success Indicators

You'll know the demo is working when you see:

- ✅ All prerequisite checks pass
- ✅ Backend starts successfully on port 8000
- ✅ Frontend starts successfully on port 3000
- ✅ All demo URLs are accessible
- ✅ Agent status shows as "ACTIVE"
- ✅ Real-time updates work in the dashboard

## 🔄 Stopping the Demo

To stop the demo:
1. Press `Ctrl+C` in the terminal
2. The script will gracefully shut down both servers
3. You'll see confirmation messages for each service

## 📝 Development Notes

### **For Developers**

The demo runner is designed to be:
- **Idempotent**: Can be run multiple times safely
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Robust**: Handles errors gracefully with clear messages
- **Extensible**: Easy to modify for different configurations

### **Customization**

To modify ports or other settings, edit the constants in `run_full_demo.py`:

```python
# URLs and ports
self.backend_url = "http://localhost:8000"
self.frontend_url = "http://localhost:3000"
self.backend_port = 8000
self.frontend_port = 3000
```

## 🎉 Ready for ShellHacks 2025!

This comprehensive demo runner ensures that your ShellHacks 2025 presentation will run smoothly, regardless of the environment. The automated setup and robust error handling make it perfect for live demonstrations and technical presentations.

**Happy Hacking! 🚀**
