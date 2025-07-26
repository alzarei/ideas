#!/usr/bin/env python3
"""
One-liner setup script that handles everything automatically
Usage: python quick_setup.py
"""

import subprocess
import sys
import os
import platform
import time

def run_command(cmd, description, check=True):
    """Run a command with description"""
    print(f"🔄 {description}...")
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Failed: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 🚀 QUICK SETUP SCRIPT 🚀                   ║
║              One command does everything!                    ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    system = platform.system().lower()
    
    # Step 1: Install Ollama if not present
    try:
        subprocess.run(['ollama', '--version'], check=True, capture_output=True)
        print("✅ Ollama already installed")
    except:
        print("🤖 Installing Ollama automatically...")
        
        if system == "windows":
            # Use winget if available, otherwise direct download
            if run_command("winget install Ollama.Ollama", "Installing Ollama via winget", check=False):
                pass
            else:
                print("📥 Downloading Ollama installer...")
                run_command("curl -L -o ollama_installer.exe https://ollama.ai/download/OllamaSetup.exe", "Downloading Ollama")
                run_command("ollama_installer.exe /S", "Installing Ollama")
                run_command("del ollama_installer.exe", "Cleaning up", check=False)
        
        elif system == "darwin":
            if not run_command("brew install ollama", "Installing Ollama via Homebrew", check=False):
                print("📥 Using direct installation...")
                run_command("curl -L https://ollama.ai/download/Ollama-darwin.zip -o ollama.zip", "Downloading Ollama")
                run_command("unzip ollama.zip", "Extracting Ollama")
                run_command("sudo mv Ollama.app /Applications/", "Installing Ollama")
                run_command("rm ollama.zip", "Cleaning up", check=False)
        
        elif system == "linux":
            run_command("curl -fsSL https://ollama.ai/install.sh | sh", "Installing Ollama for Linux")
    
    # Step 2: Set up Python environment
    if not run_command("python -m venv venv", "Creating Python virtual environment", check=False):
        run_command("python3 -m venv venv", "Creating Python virtual environment")
    
    # Step 3: Install Python dependencies
    if system == "windows":
        run_command("venv\\Scripts\\pip.exe install -r requirements.txt", "Installing Python dependencies")
    else:
        run_command("venv/bin/pip install -r requirements.txt", "Installing Python dependencies")
    
    # Step 4: Install frontend dependencies
    if os.path.exists("frontend"):
        os.chdir("frontend")
        run_command("npm install", "Installing frontend dependencies")
        run_command("npm run build", "Building frontend")
        os.chdir("..")
    
    # Step 5: Start Ollama service
    print("🚀 Starting Ollama service...")
    if system == "windows":
        subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(5)  # Wait for service to start
    
    # Step 6: Download recommended model
    run_command("ollama pull llama3.2:3b", "Downloading AI model (this may take a few minutes)")
    
    # Step 7: Create startup script
    if system == "windows":
        startup_script = """@echo off
echo Starting On-Device LLM Assistant...
cd /d "%~dp0"
if not exist "venv\\Scripts\\python.exe" (
    echo Virtual environment not found!
    pause
    exit /b 1
)
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)
call venv\\Scripts\\activate.bat
python launcher.py
pause
"""
        with open("start.bat", "w") as f:
            f.write(startup_script)
        print("✅ Created start.bat")
    else:
        startup_script = """#!/bin/bash
echo "Starting On-Device LLM Assistant..."
cd "$(dirname "$0")"
if [ ! -f "venv/bin/python" ]; then
    echo "Virtual environment not found!"
    exit 1
fi
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi
source venv/bin/activate
python launcher.py
"""
        with open("start.sh", "w") as f:
            f.write(startup_script)
        os.chmod("start.sh", 0o755)
        print("✅ Created start.sh")
    
    print("""
🎉 SETUP COMPLETE! 🎉

🚀 To start the application:
""")
    
    if system == "windows":
        print("   Double-click: start.bat")
        print("   Or run: python launcher.py")
    else:
        print("   Run: ./start.sh")
        print("   Or run: python launcher.py")
    
    print("""
📱 Access the app at: http://localhost:8000
📚 API docs at: http://localhost:8000/api/docs

🤖 Available AI models:""")
    
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        print(result.stdout)
    except:
        print("   Run 'ollama list' to see downloaded models")
    
    # Ask to start now
    try:
        choice = input("\n🚀 Start the application now? (y/n): ").lower()
        if choice in ['y', 'yes']:
            print("🚀 Starting application...")
            if system == "windows":
                subprocess.run(["venv\\Scripts\\python.exe", "launcher.py"])
            else:
                subprocess.run(["venv/bin/python", "launcher.py"])
    except KeyboardInterrupt:
        print("\n👋 Setup completed! Run the start script when ready.")

if __name__ == "__main__":
    main()
