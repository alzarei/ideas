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

def main():
    """Main launcher function"""
    print("🤖 On-Device LLM Assistant Launcher")
    print("=" * 40)
    
    # Check Ollama status
    if check_ollama():
        print("✅ Ollama is running")
    else:
        print("⚠️  Ollama not detected - API will run in demo mode")
        print("   To enable full functionality:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Download model: ollama pull llama3.2:3b")
        print("   3. Restart this application")
        print()
    
    # Install dependencies
    try:
        install_dependencies()
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Try running: pip install -r requirements.txt")
        return
    
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
