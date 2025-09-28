#!/usr/bin/env python3
"""
Install Now - Simple and Fast

This script installs just what you need to get started.
"""

import subprocess
import sys

def main():
    print("🚀 Installing Essential Packages")
    print("=" * 35)
    
    # Install essential packages one by one
    packages = ["fastapi", "uvicorn", "pydantic", "python-dotenv", "aiohttp", "websockets"]
    
    for package in packages:
        try:
            print(f"📦 Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed")
        except:
            print(f"⚠️  {package} failed - continuing...")
    
    print("\n🎉 Installation complete!")
    print("\n🧪 Test your installation:")
    print("   python test_minimal.py")

if __name__ == "__main__":
    main()
