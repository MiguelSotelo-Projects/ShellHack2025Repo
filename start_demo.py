#!/usr/bin/env python3
"""
Demo Startup Script - Starts both backend and frontend for A2A protocol demonstration
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting Ops Mesh Backend...")
    backend_dir = Path(__file__).parent / "ops-mesh-backend"
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start the backend server
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])
    
    return backend_process

def start_frontend():
    """Start the Next.js frontend"""
    print("🎨 Starting Ops Mesh Frontend...")
    frontend_dir = Path(__file__).parent / "ops-mesh-frontend"
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Start the frontend server
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ])
    
    return frontend_process

def main():
    """Main function to start both services"""
    print("🎉 Ops Mesh A2A Protocol Demo")
    print("=" * 50)
    print("This will start both the backend and frontend servers")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("Agent Demo: http://localhost:3000/agent-demo")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print()
    
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        print("✅ Backend started on http://localhost:8000")
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend
        frontend_process = start_frontend()
        print("✅ Frontend started on http://localhost:3000")
        
        print()
        print("🎯 Demo URLs:")
        print("   • Agent Demo: http://localhost:3000/agent-demo")
        print("   • Live Dashboard: http://localhost:3000/live-dashboard")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • Agent API: http://localhost:8000/api/v1/agents/status")
        print()
        print("Press Ctrl+C to stop both servers")
        print()
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
            
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
            
        print("👋 Demo stopped successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        if backend_process:
            backend_process.terminate()
            
        if frontend_process:
            frontend_process.terminate()
            
        sys.exit(1)

if __name__ == "__main__":
    main()
