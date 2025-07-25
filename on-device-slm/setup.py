#!/usr/bin/env python3
"""
One-click setup script for On-Device LLM Assistant
Automates the entire development environment setup
"""

import subprocess
import sys
import os
import platform
import webbrowser
import time
import json
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 On-Device LLM Assistant                     ║
║                    Development Setup                        ║
╚══════════════════════════════════════════════════════════════╝
""")

def check_system_requirements():
    """Check system requirements and dependencies"""
    print("🔍 Checking system requirements...")
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required (current: {}.{})".format(
            sys.version_info.major, sys.version_info.minor))
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        print(f"✅ Node.js {node_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("Node.js not found - required for frontend development")
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        npm_version = result.stdout.strip()
        print(f"✅ npm {npm_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("npm not found - comes with Node.js")
    
    # Check git
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        git_version = result.stdout.strip()
        print(f"✅ {git_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("Git not found - required for version control")
    
    return issues

def check_ollama():
    """Check if Ollama is installed and running"""
    print("\n🤖 Checking Ollama status...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Ollama installed: {result.stdout.strip()}")
        
        # Check if Ollama service is running
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                print("✅ Ollama service is running")
                
                # List available models
                models = response.json().get('models', [])
                if models:
                    print(f"✅ {len(models)} model(s) available:")
                    for model in models[:3]:  # Show first 3
                        print(f"   - {model['name']}")
                else:
                    print("⚠️  No models downloaded")
                    return "no_models"
                return "running"
            else:
                print("⚠️  Ollama service not responding")
                return "not_running"
        except Exception:
            print("⚠️  Ollama service not running")
            return "not_running"
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ollama not installed")
        return "not_installed"

def install_ollama_and_models():
    """Guide user through Ollama installation"""
    print("\n📥 Ollama Installation Required")
    print("=" * 50)
    
    system = platform.system().lower()
    
    if system == "windows":
        print("For Windows:")
        print("1. Download from: https://ollama.ai/download/windows")
        print("2. Run the installer")
        print("3. Restart your terminal/command prompt")
    elif system == "darwin":
        print("For macOS:")
        print("1. Download from: https://ollama.ai/download/mac")
        print("2. Or use Homebrew: brew install ollama")
    else:
        print("For Linux:")
        print("1. Run: curl -fsSL https://ollama.ai/install.sh | sh")
    
    print("\nAfter installation, run these commands:")
    print("  ollama serve")
    print("  ollama pull llama3.2:3b")
    
    choice = input("\nWould you like me to open the Ollama download page? (y/n): ").lower()
    if choice == 'y':
        webbrowser.open("https://ollama.ai/download")
    
    return False

def setup_python_environment():
    """Set up Python virtual environment and install dependencies"""
    print("\n🐍 Setting up Python environment...")
    
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment exists")
    
    # Determine activation script
    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Install dependencies
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print("Installing Python dependencies...")
        subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
        print("✅ Python dependencies installed")
    
    return python_path, pip_path

def setup_frontend():
    """Set up React frontend"""
    print("\n⚛️  Setting up React frontend...")
    
    frontend_path = Path(__file__).parent / "frontend"
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_path)
    
    # Install npm dependencies
    if (frontend_path / "package.json").exists():
        print("Installing npm dependencies...")
        subprocess.run(["npm", "install"], check=True)
        print("✅ npm dependencies installed")
        
        # Build frontend
        print("Building frontend...")
        subprocess.run(["npm", "run", "build"], check=True)
        print("✅ Frontend built successfully")
        
        return True
    else:
        print("❌ package.json not found")
        return False

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n📜 Creating startup scripts...")
    
    project_root = Path(__file__).parent
    
    # Create Windows batch file
    if platform.system() == "Windows":
        batch_content = """@echo off
echo Starting On-Device LLM Assistant...
cd /d "%~dp0"

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Start the application
python launcher.py

pause
"""
        with open(project_root / "start.bat", "w") as f:
            f.write(batch_content)
        print("✅ Created start.bat")
    
    # Create Unix shell script
    bash_content = """#!/bin/bash
echo "Starting On-Device LLM Assistant..."
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the application
python launcher.py
"""
    with open(project_root / "start.sh", "w") as f:
        f.write(bash_content)
    
    # Make shell script executable
    if platform.system() != "Windows":
        os.chmod(project_root / "start.sh", 0o755)
        print("✅ Created start.sh")

def create_development_guide():
    """Create a quick development guide"""
    print("\n📖 Creating development guide...")
    
    guide_content = """# Quick Development Guide

## Project Structure
```
├── backend/           # FastAPI backend
├── frontend/          # React TypeScript frontend
├── config/           # Model and training configuration
├── examples/         # Usage examples
├── venv/            # Python virtual environment
└── launcher.py      # Main application launcher
```

## Quick Start

### Option 1: Use Startup Scripts
- **Windows**: Double-click `start.bat`
- **Mac/Linux**: Run `./start.sh`

### Option 2: Manual Start
```bash
# Activate virtual environment
source venv/bin/activate          # Mac/Linux
# OR
venv\\Scripts\\activate            # Windows

# Start application
python launcher.py
```

## Development Workflow

### Backend Development
```bash
# Activate environment
source venv/bin/activate

# Start backend only
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# In a separate terminal
cd frontend
npm start
```

### Adding New Models
1. Edit `config/models.json`
2. Add model configuration
3. Pull model: `ollama pull model-name`
4. Restart application

## API Endpoints
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health

## Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Pull a model
ollama pull llama3.2:3b
```

### Python Issues
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Next Steps
1. Visit http://localhost:8000 to use the application
2. Check out examples in the `examples/` directory
3. Read `ARCHITECTURE.md` for system overview
4. Explore `config/models.json` for model options
"""

    with open(Path(__file__).parent / "DEVELOPMENT.md", "w") as f:
        f.write(guide_content)
    
    print("✅ Created DEVELOPMENT.md")

def main():
    """Main setup function"""
    print_banner()
    
    # Check system requirements
    issues = check_system_requirements()
    if issues:
        print("\n❌ System Requirements Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease resolve these issues and run setup again.")
        return False
    
    # Check Ollama
    ollama_status = check_ollama()
    if ollama_status == "not_installed":
        install_ollama_and_models()
        print("\nPlease install Ollama and run this setup again.")
        return False
    elif ollama_status == "not_running":
        print("\n⚠️  Ollama is installed but not running.")
        print("Please start Ollama service: ollama serve")
        print("Then run this setup again.")
    elif ollama_status == "no_models":
        print("\n📥 Downloading recommended model...")
        try:
            subprocess.run(["ollama", "pull", "llama3.2:3b"], check=True)
            print("✅ Model downloaded successfully")
        except subprocess.CalledProcessError:
            print("⚠️  Failed to download model. You can do this manually:")
            print("   ollama pull llama3.2:3b")
    
    try:
        # Setup Python environment
        python_path, pip_path = setup_python_environment()
        
        # Setup frontend
        current_dir = os.getcwd()
        frontend_success = setup_frontend()
        os.chdir(current_dir)  # Return to project root
        
        if not frontend_success:
            print("⚠️  Frontend setup failed, but backend will still work")
        
        # Create startup scripts
        create_startup_scripts()
        
        # Create development guide
        create_development_guide()
        
        print("\n" + "="*60)
        print("🎉 Setup completed successfully!")
        print("="*60)
        print("\n🚀 To start the application:")
        if platform.system() == "Windows":
            print("   Double-click: start.bat")
        else:
            print("   Run: ./start.sh")
        print("   Or: python launcher.py")
        
        print("\n📚 Next steps:")
        print("   1. Read DEVELOPMENT.md for development guide")
        print("   2. Visit http://localhost:8000 once started")
        print("   3. Explore examples/ directory")
        
        # Ask if user wants to start now
        choice = input("\nWould you like to start the application now? (y/n): ").lower()
        if choice == 'y':
            print("\n🚀 Starting application...")
            subprocess.run([sys.executable, "launcher.py"])
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check the error above and try again.")
        return False

if __name__ == "__main__":
    main()
