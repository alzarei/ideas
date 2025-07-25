#!/usr/bin/env python3
"""
Launcher for On-Device LLM Assistant
Starts the FastAPI backend and opens the application
"""

import subprocess
import webbrowser
import time
import sys
import os
from pathlib import Path

def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ Dependencies installed!")
    else:
        print("❌ requirements.txt not found!")
        return False
    return True

def start_backend():
    """Start the FastAPI backend server"""
    backend_dir = Path(__file__).parent / "backend"
    main_file = backend_dir / "main.py"
    
    if not main_file.exists():
        print("❌ Backend main.py not found!")
        return None
    
    print("🚀 Starting FastAPI backend...")
    os.chdir(backend_dir)
    
    # Start FastAPI server
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload"
    ])
    
    return process

def warning_mark(message):
    """Print warning symbol"""
    print(f"⚠️  {message}")

def info_mark(message):
    """Print info symbol"""
    print(f"ℹ️  {message}")

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import requests
        return True
    except ImportError:
        return False

def check_frontend_build():
    """Check if frontend is built"""
    frontend_build = Path(__file__).parent / "frontend" / "build"
    return frontend_build.exists()

def prompt_setup():
    """Prompt user to run setup if dependencies are missing"""
    print("🔧 Dependencies not found!")
    print("It looks like the project hasn't been set up yet.")
    print()
    print("Quick setup options:")
    print("1. Run automated setup: python setup.py")
    print("2. Manual install: pip install -r requirements.txt")
    print("3. PowerShell script: .\\dev.ps1 setup")
    print("4. Make: make setup")
    print()
    
    choice = input("Would you like to run automated setup now? (y/n): ").lower()
    if choice == 'y':
        print("\n🚀 Running setup...")
        try:
            subprocess.run([sys.executable, "setup.py"], check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Setup failed. Please try manual installation.")
            return False
    return False

def main():
    """Main launcher function"""
    print("🤖 On-Device LLM Assistant Launcher")
    print("=" * 40)
    
    # Check dependencies first
    if not check_dependencies():
        if not prompt_setup():
            print("\n📖 Setup required before starting.")
            print("Run 'python setup.py' or see README.md for instructions.")
            return
        
        # Re-check after setup
        if not check_dependencies():
            print("❌ Dependencies still missing after setup.")
            return
    
    # Check frontend build
    if not check_frontend_build():
        warning_mark("Frontend not built for production")
        info_mark("For full functionality, run: cd frontend && npm run build")
    
    # Check Ollama status
    if check_ollama():
        print("✅ Ollama is running")
    else:
        print("⚠️  Ollama not detected - API will run in demo mode")
        print("   To enable full functionality:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Start service: ollama serve")
        print("   3. Download model: ollama pull llama3.2:3b")
        print("   4. Restart this application")
        print()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        return
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Open browser
    url = "http://localhost:8000"
    print(f"🌐 Opening browser: {url}")
    webbrowser.open(url)
    
    print("\n✅ Application started successfully!")
    print("📖 API Documentation: http://localhost:8000/api/docs")
    print("🏥 Health Check: http://localhost:8000/api/health")
    print("🔍 Verify Installation: python verify.py")
    print("\n🛑 Press Ctrl+C to stop the server")
    
    try:
        # Keep the launcher running
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()
