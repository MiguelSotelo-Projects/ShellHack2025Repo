#!/usr/bin/env python3
"""
Test runner script for the ops-mesh-backend project.

This script provides various options for running tests:
- Run all tests
- Run specific test categories
- Run with coverage
- Run with different verbosity levels
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for ops-mesh-backend")
    parser.add_argument(
        "--category", 
        choices=["all", "unit", "api", "model", "service", "agent", "integration"],
        default="all",
        help="Test category to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests"
    )
    parser.add_argument(
        "--file",
        help="Run specific test file"
    )
    parser.add_argument(
        "--function",
        help="Run specific test function"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies first"
    )
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    import os
    os.chdir(project_dir)
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        install_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        if not run_command(install_cmd, "Installing dependencies"):
            return 1
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-vv")
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add category-specific markers
    if args.category != "all":
        cmd.extend(["-m", args.category])
    
    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Add specific file or function
    if args.file:
        cmd.append(f"tests/{args.file}")
    elif args.function:
        cmd.extend(["-k", args.function])
    else:
        cmd.append("tests/")
    
    # Run the tests
    success = run_command(cmd, f"Running {args.category} tests")
    
    if args.coverage and success:
        print(f"\n📊 Coverage report generated in htmlcov/index.html")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
