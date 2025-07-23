#!/usr/bin/env python3
"""
Installation verification script for On-Device LLM Assistant
Checks if all components are properly installed and configured
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_mark(condition, message):
    """Print check mark or X based on condition"""
    symbol = "✅" if condition else "❌"
    print(f"{symbol} {message}")
    return condition

def warning_mark(message):
    """Print warning symbol"""
    print(f"⚠️  {message}")

def info_mark(message):
    """Print info symbol"""
    print(f"ℹ️  {message}")

def check_python_environment():
    """Verify Python environment"""
    print_header("Python Environment")
    
    # Check Python version
    version_ok = check_mark(
        sys.version_info >= (3, 8),
        f"Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    
    # Check virtual environment
    venv_path = Path("venv")
    venv_exists = check_mark(venv_path.exists(), "Virtual environment exists")
    
    # Check if we're in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv and venv_exists:
        warning_mark("Not running in virtual environment")
        info_mark("Activate with: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Unix)")
    
    # Check required packages
    required_packages = [
        'fastapi', 'uvicorn', 'requests', 'psutil', 'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            check_mark(True, f"{package} installed")
        except ImportError:
            check_mark(False, f"{package} installed")
            missing_packages.append(package)
    
    if missing_packages:
        warning_mark(f"Missing packages: {', '.join(missing_packages)}")
        info_mark("Install with: pip install -r requirements.txt")
    
    return version_ok and venv_exists and len(missing_packages) == 0

def check_node_environment():
    """Verify Node.js environment"""
    print_header("Node.js Environment")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        node_version = result.stdout.strip()
        check_mark(True, f"Node.js {node_version}")
        node_ok = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        check_mark(False, "Node.js not found")
        info_mark("Install from: https://nodejs.org")
        node_ok = False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        npm_version = result.stdout.strip()
        check_mark(True, f"npm {npm_version}")
        npm_ok = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        check_mark(False, "npm not found")
        npm_ok = False
    
    # Check frontend dependencies
    frontend_path = Path("frontend")
    package_json_exists = check_mark(
        (frontend_path / "package.json").exists(),
        "package.json exists"
    )
    
    node_modules_exists = check_mark(
        (frontend_path / "node_modules").exists(),
        "node_modules installed"
    )
    
    if package_json_exists and not node_modules_exists:
        warning_mark("Frontend dependencies not installed")
        info_mark("Run: cd frontend && npm install")
    
    # Check if frontend is built
    build_exists = check_mark(
        (frontend_path / "build").exists(),
        "Frontend build exists"
    )
    
    if not build_exists and node_modules_exists:
        warning_mark("Frontend not built for production")
        info_mark("Run: cd frontend && npm run build")
    
    return node_ok and npm_ok and package_json_exists

def check_ollama():
    """Verify Ollama installation and models"""
    print_header("Ollama Environment")
    
    # Check Ollama command
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=True)
        ollama_version = result.stdout.strip()
        check_mark(True, f"Ollama {ollama_version}")
        ollama_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        check_mark(False, "Ollama command not found")
        info_mark("Install from: https://ollama.ai")
        return False
    
    # Check if Ollama service is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            check_mark(True, "Ollama service is running")
            
            # Check available models
            models = response.json().get('models', [])
            if models:
                check_mark(True, f"{len(models)} model(s) available")
                print("   Available models:")
                for model in models[:5]:  # Show first 5
                    print(f"     - {model['name']}")
                if len(models) > 5:
                    print(f"     ... and {len(models) - 5} more")
                return True
            else:
                check_mark(False, "No models downloaded")
                warning_mark("Download a model with: ollama pull llama3.2:3b")
                return False
        else:
            check_mark(False, "Ollama service not responding")
            warning_mark("Start with: ollama serve")
            return False
    except Exception as e:
        check_mark(False, "Ollama service not running")
        warning_mark("Start with: ollama serve")
        return False

def check_project_structure():
    """Verify project structure and configuration"""
    print_header("Project Structure")
    
    required_files = [
        "launcher.py",
        "requirements.txt",
        "backend/main.py",
        "config/models.json",
        "config/model_manager.py",
        "frontend/package.json"
    ]
    
    all_present = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        check_mark(exists, f"{file_path}")
        if not exists:
            all_present = False
    
    # Check configuration files
    models_config_path = Path("config/models.json")
    if models_config_path.exists():
        try:
            with open(models_config_path) as f:
                config = json.load(f)
                models = config.get('models', [])
                enabled_models = [m for m in models if m.get('enabled', False)]
                check_mark(
                    len(enabled_models) > 0,
                    f"{len(enabled_models)} model(s) enabled in configuration"
                )
        except Exception:
            check_mark(False, "models.json is valid JSON")
    
    return all_present

def check_startup_scripts():
    """Verify startup scripts are present"""
    print_header("Startup Scripts")
    
    startup_files = [
        ("setup.py", "Automated setup script"),
        ("dev.ps1", "PowerShell development script"),
        ("Makefile", "Make development tasks"),
        ("launcher.py", "Application launcher")
    ]
    
    all_present = True
    for file_path, description in startup_files:
        exists = Path(file_path).exists()
        check_mark(exists, f"{description} ({file_path})")
        if not exists:
            all_present = False
    
    return all_present

def check_development_setup():
    """Check if development environment is properly configured"""
    print_header("Development Setup")
    
    # Check if git is available
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        git_version = result.stdout.strip()
        check_mark(True, f"{git_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        check_mark(False, "Git not found")
        warning_mark("Git is recommended for development")
    
    # Check documentation files
    docs = [
        "README.md",
        "DEVELOPMENT.md",
        "ARCHITECTURE.md"
    ]
    
    for doc in docs:
        exists = Path(doc).exists()
        check_mark(exists, f"{doc} documentation")

def main():
    """Main verification function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Installation Verification Report               ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    results = {
        'python': check_python_environment(),
        'node': check_node_environment(),
        'ollama': check_ollama(),
        'structure': check_project_structure(),
        'scripts': check_startup_scripts()
    }
    
    check_development_setup()
    
    # Summary
    print_header("Verification Summary")
    
    all_good = all(results.values())
    
    for component, status in results.items():
        check_mark(status, f"{component.title()} environment")
    
    if all_good:
        print("\n🎉 All components verified successfully!")
        print("\n🚀 Ready to start:")
        print("   python launcher.py")
        print("   OR")
        print("   .\\dev.ps1 start     (Windows)")
        print("   make start          (Unix/Linux/macOS)")
    else:
        print("\n⚠️  Some issues found. Please resolve them and run verification again.")
        print("\n💡 Quick fixes:")
        if not results['python']:
            print("   Python: pip install -r requirements.txt")
        if not results['node']:
            print("   Node.js: cd frontend && npm install && npm run build")
        if not results['ollama']:
            print("   Ollama: ollama serve && ollama pull llama3.2:3b")
    
    print(f"\n📊 Overall Status: {'READY' if all_good else 'NEEDS ATTENTION'}")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
