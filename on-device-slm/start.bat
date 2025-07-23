@echo off
REM On-Device LLM Assistant - Windows Startup Script
REM This script provides an easy way to start the application on Windows

title On-Device LLM Assistant

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                 On-Device LLM Assistant                     ║
echo ║                    Windows Launcher                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔧 Virtual environment not found. Running setup...
    python setup.py
    if %errorlevel% neq 0 (
        echo ❌ Setup failed!
        pause
        exit /b 1
    )
)

REM Activate virtual environment and start application
echo 🚀 Starting On-Device LLM Assistant...
call venv\Scripts\activate.bat
python launcher.py

echo.
echo 👋 Thanks for using On-Device LLM Assistant!
pause
