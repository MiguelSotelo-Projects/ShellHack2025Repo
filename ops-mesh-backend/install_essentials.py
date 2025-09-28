#!/usr/bin/env python3
"""
Essential Dependencies Installer

This script installs only the essential packages needed to get the system running.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package"""
    try:
        print(f"📦 Installing {package}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], check=True, capture_output=True, text=True, timeout=60)
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}")
        return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout installing {package}")
        return False

def main():
    print("🚀 Installing Essential Dependencies")
    print("=" * 40)
    
    # Essential packages only
    essential_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "python-dotenv",
        "aiohttp",
        "websockets"
    ]
    
    print("📋 Installing essential packages only...")
    print("This will be much faster than the full installation.")
    print()
    
    success_count = 0
    for package in essential_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(essential_packages)} packages installed")
    
    if success_count >= 4:  # At least 4 out of 6 essential packages
        print("\n✅ Essential packages installed successfully!")
        print("\n🎯 You can now test the basic system:")
        print("   python -c \"import fastapi; print('FastAPI works!')\"")
        print("   python -c \"import aiohttp; print('aiohttp works!')\"")
        
        print("\n📝 Next steps:")
        print("   1. Test basic functionality")
        print("   2. Install additional packages as needed")
        print("   3. Run: python setup_a2a.py --setup")
    else:
        print("\n⚠️  Some essential packages failed to install")
        print("   You may need to install them manually or check your Python environment")

if __name__ == "__main__":
    main()
