#!/bin/bash
# On-Device LLM Assistant - Unix/Linux/macOS Startup Script
# This script provides an easy way to start the application

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 On-Device LLM Assistant                     ║"
echo "║                     Unix Launcher                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python not found!"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Using Python: $($PYTHON_CMD --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Virtual environment not found. Running setup..."
    $PYTHON_CMD setup.py
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed!"
        exit 1
    fi
fi

# Activate virtual environment and start application
echo "🚀 Starting On-Device LLM Assistant..."
source venv/bin/activate
$PYTHON_CMD launcher.py

echo ""
echo "👋 Thanks for using On-Device LLM Assistant!"
