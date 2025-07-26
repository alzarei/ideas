#!/usr/bin/env python3
"""
Quick Setup - Skip large model downloads initially
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_banner():
    print("""
+==============================================================+
|                 QUICK SETUP (No Models)                     |
|                 On-Device LLM Assistant                     |
+==============================================================+
""")

def main():
    print_banner()
    print("Running quick setup without model downloads...")
    print("   (You can download models later when the app is running)")
    
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
echo Starting On-Device LLM Assistant (Quick Mode)...
cd /d "%~dp0"

echo Note: No AI models installed yet.
echo You can download models from the web interface once the app starts.

call venv\\Scripts\\activate.bat
python launcher.py
pause
'''
        with open("start_quick.bat", "w") as f:
            f.write(startup_content)
        print("[OK] Created start_quick.bat")
    
    print("\n" + "="*60)
    print("Setup completed successfully!")
    print("="*60)
    print("\nTo start the application:")
    if platform.system() == "Windows":
        print("   Double-click: start_quick.bat")
    print("   Or run: python launcher.py")
    print("\nNote: No AI models are installed yet.")
    print("   You can download them from the web interface or run:")
    print("   ollama pull llama3.2:1b  (small model)")
    
    # Automatically start the application
    print("\nStarting application automatically...")
    try:
        if platform.system() == "Windows":
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            python_path = venv_path / "bin" / "python"
        
        subprocess.run([str(python_path), "launcher.py"])
    except Exception as e:
        print(f"Failed to start application: {e}")
        print("You can start it manually with: python launcher.py")
    
    return True

if __name__ == "__main__":
    main()
