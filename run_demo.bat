@echo off
REM ShellHacks 2025 - Windows Demo Runner
REM This is a simple wrapper for Windows users

echo 🎉 ShellHacks 2025 - Ops Mesh Demo
echo ====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if the Python script exists
if not exist "run_full_demo.py" (
    echo ❌ run_full_demo.py not found
    echo Please make sure you're in the correct directory
    pause
    exit /b 1
)

REM Run the main Python script
echo 🚀 Starting the demo...
python run_full_demo.py

REM Pause to show any error messages
if errorlevel 1 (
    echo.
    echo ❌ Demo failed to start
    pause
)
