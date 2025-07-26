#!/usr/bin/env python3
"""
Ultra Quick Setup - Fully automatic, no prompts, no UTF-8 characters
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_banner():
    print("""
+==============================================================+
|                ULTRA QUICK SETUP                            |
|                On-Device LLM Assistant                      |
|               Fully Automatic - No Prompts                 |
+==============================================================+
""")

def main():
    print_banner()
    print("Running fully automatic setup...")
    print("No user input required - everything happens automatically")
    
    # Check if Python environment exists
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    if not venv_path.exists():
        print("\n[ERROR] Virtual environment not found")
        print("Please run 'python setup_improved.py' first")
        return False
    
    # Check frontend build
    frontend_build = project_root / "frontend" / "build"
    if not frontend_build.exists():
        print("\n[ERROR] Frontend build not found") 
        print("Please run 'python setup_improved.py' first to build frontend")
        return False
    
    print("\n[OK] Python environment: Ready")
    print("[OK] Frontend build: Ready")
    
    # Create startup script
    if platform.system() == "Windows":
        startup_content = '''@echo off
echo Starting On-Device LLM Assistant...
cd /d "%~dp0"

echo Checking for Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
)

call venv\\Scripts\\activate.bat
python launcher.py
pause
'''
        with open("start_auto.bat", "w") as f:
            f.write(startup_content)
        print("[OK] Created start_auto.bat")
    else:
        startup_content = '''#!/bin/bash
echo "Starting On-Device LLM Assistant..."
cd "$(dirname "$0")"

echo "Checking for Ollama service..."
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 3
fi

source venv/bin/activate
python launcher.py
'''
        with open("start_auto.sh", "w") as f:
            f.write(startup_content)
        os.chmod("start_auto.sh", 0o755)
        print("[OK] Created start_auto.sh")
    
    print("\n" + "="*60)
    print("Setup completed successfully!")
    print("="*60)
    print("\nApplication starting automatically...")
    
    if platform.system() == "Windows":
        print("Future starts: Double-click start_auto.bat")
    else:
        print("Future starts: Run ./start_auto.sh")
    
    print("\nNote: AI models can be downloaded from the web interface")
    print("or manually with: ollama pull llama3.2:1b")
    
    # Automatically start the application
    print("\nLaunching application now...")
    try:
        if platform.system() == "Windows":
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            python_path = venv_path / "bin" / "python"
        
        # Start the application
        print("Starting launcher...")
        subprocess.run([str(python_path), "launcher.py"])
        
    except Exception as e:
        print(f"[ERROR] Failed to start application: {e}")
        print("You can start it manually with: python launcher.py")
        return False
    
    return True

if __name__ == "__main__":
    main()
