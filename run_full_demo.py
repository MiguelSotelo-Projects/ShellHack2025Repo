#!/usr/bin/env python3
"""
ShellHacks 2025 - Complete Demo Runner
=====================================

This script provides a comprehensive solution to run the entire Ops Mesh A2A Protocol Demo.
It handles:
- Dependency checking and installation
- Database setup
- Backend and frontend startup
- Process management and cleanup
- Cross-platform compatibility

Usage:
    python run_full_demo.py [--setup-only] [--skip-setup] [--help]

Options:
    --setup-only    Only run setup, don't start the demo
    --skip-setup    Skip setup and go directly to running the demo
    --help          Show this help message
"""

import subprocess
import sys
import time
import os
import signal
import platform
import argparse
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading
import requests
from urllib.parse import urljoin

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class DemoRunner:
    """Main class for running the complete demo"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "ops-mesh-backend"
        self.frontend_dir = self.root_dir / "ops-mesh-frontend"
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.setup_complete = False
        
        # URLs and ports
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.backend_port = 8000
        self.frontend_port = 3000
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def log(self, message: str, color: str = Colors.WHITE, bold: bool = False):
        """Print colored log message"""
        style = Colors.BOLD if bold else ""
        print(f"{style}{color}{message}{Colors.END}")
    
    def log_success(self, message: str):
        """Print success message"""
        self.log(f"✅ {message}", Colors.GREEN)
    
    def log_error(self, message: str):
        """Print error message"""
        self.log(f"❌ {message}", Colors.RED, bold=True)
    
    def log_warning(self, message: str):
        """Print warning message"""
        self.log(f"⚠️  {message}", Colors.YELLOW)
    
    def log_info(self, message: str):
        """Print info message"""
        self.log(f"ℹ️  {message}", Colors.CYAN)
    
    def log_step(self, message: str):
        """Print step message"""
        self.log(f"🔧 {message}", Colors.BLUE)
    
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        self.log_step("Checking prerequisites...")
        
        # Check Python
        if not shutil.which("python3") and not shutil.which("python"):
            self.log_error("Python 3 is not installed or not in PATH")
            return False
        
        # Check Node.js
        if not shutil.which("npm"):
            self.log_error("Node.js/npm is not installed or not in PATH")
            return False
        
        # Check if directories exist
        if not self.backend_dir.exists():
            self.log_error(f"Backend directory not found: {self.backend_dir}")
            return False
        
        if not self.frontend_dir.exists():
            self.log_error(f"Frontend directory not found: {self.frontend_dir}")
            return False
        
        self.log_success("Prerequisites check passed")
        return True
    
    def check_ports_available(self) -> bool:
        """Check if required ports are available"""
        self.log_step("Checking port availability...")
        
        import socket
        
        def is_port_available(port: int) -> bool:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return True
                except OSError:
                    return False
        
        if not is_port_available(self.backend_port):
            self.log_error(f"Port {self.backend_port} is already in use")
            return False
        
        if not is_port_available(self.frontend_port):
            self.log_error(f"Port {self.frontend_port} is already in use")
            return False
        
        self.log_success("Ports are available")
        return True
    
    def setup_backend(self) -> bool:
        """Setup backend dependencies and database"""
        self.log_step("Setting up backend...")
        
        try:
            # Change to backend directory
            os.chdir(self.backend_dir)
            
            # Create virtual environment if it doesn't exist
            venv_path = self.backend_dir / "venv"
            if not venv_path.exists():
                self.log_info("Creating Python virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            
            # Determine activation script based on platform
            if platform.system() == "Windows":
                activate_script = venv_path / "Scripts" / "activate.bat"
                python_executable = venv_path / "Scripts" / "python.exe"
                pip_executable = venv_path / "Scripts" / "pip.exe"
            else:
                activate_script = venv_path / "bin" / "activate"
                python_executable = venv_path / "bin" / "python"
                pip_executable = venv_path / "bin" / "pip"
            
            # Install dependencies
            self.log_info("Installing Python dependencies...")
            subprocess.run([str(pip_executable), "install", "-r", "requirements.txt"], check=True)
            
            # Create database
            self.log_info("Setting up database...")
            db_setup_code = """
from app.core.database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database created successfully')
"""
            subprocess.run([str(python_executable), "-c", db_setup_code], check=True)
            
            self.log_success("Backend setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"Backend setup failed: {e}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error during backend setup: {e}")
            return False
        finally:
            # Return to root directory
            os.chdir(self.root_dir)
    
    def setup_frontend(self) -> bool:
        """Setup frontend dependencies"""
        self.log_step("Setting up frontend...")
        
        try:
            # Change to frontend directory
            os.chdir(self.frontend_dir)
            
            # Install Node.js dependencies
            node_modules_path = self.frontend_dir / "node_modules"
            if not node_modules_path.exists():
                self.log_info("Installing Node.js dependencies...")
                subprocess.run(["npm", "install"], check=True)
            else:
                self.log_info("Node.js dependencies already installed")
            
            self.log_success("Frontend setup completed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log_error(f"Frontend setup failed: {e}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error during frontend setup: {e}")
            return False
        finally:
            # Return to root directory
            os.chdir(self.root_dir)
    
    def wait_for_service(self, url: str, service_name: str, timeout: int = 30) -> bool:
        """Wait for a service to become available"""
        self.log_info(f"Waiting for {service_name} to start...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    self.log_success(f"{service_name} is ready")
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(1)
        
        self.log_error(f"{service_name} failed to start within {timeout} seconds")
        return False
    
    def start_backend(self) -> bool:
        """Start the backend server"""
        self.log_step("Starting backend server...")
        
        try:
            # Change to backend directory
            os.chdir(self.backend_dir)
            
            # Determine Python executable based on platform
            if platform.system() == "Windows":
                python_executable = self.backend_dir / "venv" / "Scripts" / "python.exe"
            else:
                python_executable = self.backend_dir / "venv" / "bin" / "python"
            
            # Start the backend server
            self.backend_process = subprocess.Popen([
                str(python_executable), "-m", "uvicorn",
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", str(self.backend_port),
                "--reload"
            ])
            
            # Wait for backend to be ready
            if self.wait_for_service(f"{self.backend_url}/health", "Backend"):
                self.log_success(f"Backend started on {self.backend_url}")
                return True
            else:
                return False
                
        except Exception as e:
            self.log_error(f"Failed to start backend: {e}")
            return False
        finally:
            # Return to root directory
            os.chdir(self.root_dir)
    
    def start_frontend(self) -> bool:
        """Start the frontend server"""
        self.log_step("Starting frontend server...")
        
        try:
            # Change to frontend directory
            os.chdir(self.frontend_dir)
            
            # Start the frontend server
            self.frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ])
            
            # Wait for frontend to be ready
            if self.wait_for_service(self.frontend_url, "Frontend", timeout=60):
                self.log_success(f"Frontend started on {self.frontend_url}")
                return True
            else:
                return False
                
        except Exception as e:
            self.log_error(f"Failed to start frontend: {e}")
            return False
        finally:
            # Return to root directory
            os.chdir(self.root_dir)
    
    def print_demo_info(self):
        """Print demo information and URLs"""
        self.log("\n" + "="*60, Colors.CYAN, bold=True)
        self.log("🎉 Ops Mesh A2A Protocol Demo is Running!", Colors.CYAN, bold=True)
        self.log("="*60, Colors.CYAN, bold=True)
        
        self.log("\n🌐 Available URLs:", Colors.WHITE, bold=True)
        self.log(f"   • Main Dashboard: {self.frontend_url}", Colors.GREEN)
        self.log(f"   • Enhanced Dashboard: {self.frontend_url}/enhanced-dashboard", Colors.GREEN)
        self.log(f"   • Agent Demo: {self.frontend_url}/agent-demo", Colors.GREEN)
        self.log(f"   • Live Dashboard: {self.frontend_url}/live-dashboard", Colors.GREEN)
        self.log(f"   • Patient Flow: {self.frontend_url}/patient-flow", Colors.GREEN)
        self.log(f"   • API Documentation: {self.backend_url}/docs", Colors.GREEN)
        self.log(f"   • Health Check: {self.backend_url}/health", Colors.GREEN)
        
        self.log("\n✨ Features Available:", Colors.WHITE, bold=True)
        self.log("   • Visual agent status monitoring", Colors.YELLOW)
        self.log("   • Patient management with status updates", Colors.YELLOW)
        self.log("   • Queue management with dequeue operations", Colors.YELLOW)
        self.log("   • Real-time statistics and activity logs", Colors.YELLOW)
        self.log("   • A2A protocol workflow testing", Colors.YELLOW)
        self.log("   • Agent-to-agent communication", Colors.YELLOW)
        
        self.log("\n🎯 Quick Start:", Colors.WHITE, bold=True)
        self.log("   1. Open the Main Dashboard to see the overview", Colors.CYAN)
        self.log("   2. Try the Agent Demo to test A2A communication", Colors.CYAN)
        self.log("   3. Use Patient Flow to register walk-ins", Colors.CYAN)
        self.log("   4. Check the API docs for technical details", Colors.CYAN)
        
        self.log(f"\n🛑 Press Ctrl+C to stop the demo", Colors.RED, bold=True)
        self.log("="*60, Colors.CYAN, bold=True)
    
    def monitor_processes(self):
        """Monitor running processes and handle cleanup"""
        try:
            while True:
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    self.log_error("Backend process stopped unexpectedly")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    self.log_error("Frontend process stopped unexpectedly")
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
    
    def cleanup(self):
        """Clean up running processes"""
        self.log("\n🛑 Shutting down demo...", Colors.YELLOW, bold=True)
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                self.log_success("Backend stopped")
            except subprocess.TimeoutExpired:
                self.log_warning("Backend didn't stop gracefully, forcing...")
                self.backend_process.kill()
            except Exception as e:
                self.log_error(f"Error stopping backend: {e}")
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                self.log_success("Frontend stopped")
            except subprocess.TimeoutExpired:
                self.log_warning("Frontend didn't stop gracefully, forcing...")
                self.frontend_process.kill()
            except Exception as e:
                self.log_error(f"Error stopping frontend: {e}")
        
        self.log("👋 Demo stopped successfully!", Colors.GREEN, bold=True)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self.cleanup()
        sys.exit(0)
    
    def run_setup(self) -> bool:
        """Run the complete setup process"""
        self.log("🚀 Starting Ops Mesh Demo Setup", Colors.CYAN, bold=True)
        self.log("="*50, Colors.CYAN)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Check port availability
        if not self.check_ports_available():
            return False
        
        # Setup backend
        if not self.setup_backend():
            return False
        
        # Setup frontend
        if not self.setup_frontend():
            return False
        
        self.setup_complete = True
        self.log_success("Setup completed successfully!")
        return True
    
    def run_demo(self) -> bool:
        """Run the complete demo"""
        if not self.setup_complete:
            self.log_warning("Setup not completed, running setup first...")
            if not self.run_setup():
                return False
        
        # Start backend
        if not self.start_backend():
            return False
        
        # Start frontend
        if not self.start_frontend():
            return False
        
        # Print demo information
        self.print_demo_info()
        
        # Monitor processes
        try:
            self.monitor_processes()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ShellHacks 2025 - Complete Ops Mesh A2A Protocol Demo Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_full_demo.py              # Run complete setup and demo
  python run_full_demo.py --setup-only # Only run setup
  python run_full_demo.py --skip-setup # Skip setup, run demo only
        """
    )
    
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only run setup, don't start the demo"
    )
    
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip setup and go directly to running the demo"
    )
    
    args = parser.parse_args()
    
    # Create demo runner instance
    runner = DemoRunner()
    
    try:
        if args.setup_only:
            # Only run setup
            success = runner.run_setup()
        elif args.skip_setup:
            # Skip setup, run demo only
            runner.setup_complete = True
            success = runner.run_demo()
        else:
            # Run complete setup and demo
            success = runner.run_demo()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        runner.cleanup()
        sys.exit(0)
    except Exception as e:
        runner.log_error(f"Unexpected error: {e}")
        runner.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
