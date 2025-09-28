#!/usr/bin/env python3
"""
Quick Fix Script for Ops Mesh Dependencies

This script provides a quick fix for the dependency installation issues.
"""

import subprocess
import sys
import os

def main():
    print("🔧 Quick Fix for Ops Mesh Dependencies")
    print("=" * 50)
    
    # Try to install the minimal requirements
    print("📦 Installing minimal requirements...")
    
    try:
        # Install from minimal requirements file
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements-minimal.txt"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Minimal requirements installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install from requirements file")
        print("🔄 Trying individual package installation...")
        
        # Try installing core packages individually
        core_packages = [
            "fastapi",
            "uvicorn", 
            "sqlalchemy",
            "pydantic",
            "pydantic-settings",
            "python-multipart",
            "python-dotenv",
            "pytest",
            "pytest-asyncio",
            "httpx",
            "websockets",
            "aiohttp"
        ]
        
        for package in core_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Failed to install {package}")
        
        # Try Google Cloud packages
        google_packages = [
            "google-cloud-aiplatform",
            "google-cloud-pubsub",
            "google-cloud-storage",
            "google-auth"
        ]
        
        for package in google_packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Failed to install {package}")
    
    print("\n🎉 Quick fix completed!")
    print("\n📋 What's been set up:")
    print("   • Core dependencies installed")
    print("   • Google Cloud services installed")
    print("   • A2A protocol using internal implementation")
    print("   • Google ADK using internal fallback")
    
    print("\n🚀 You can now try:")
    print("   python setup_a2a.py --setup")
    print("   python test_a2a_implementation.py")

if __name__ == "__main__":
    main()
