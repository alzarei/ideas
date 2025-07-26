#!/usr/bin/env python3
"""
Enhanced One-click setup script for On-Device LLM Assistant
Fully automates Ollama installation and model downloads
"""

import subprocess
import sys
import os
import platform
import webbrowser
import time
import json
import urllib.request
import tempfile
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("""
+==============================================================+
|                 On-Device LLM Assistant                     |
|              Enhanced Automated Setup                       |
+==============================================================+
""")

def is_admin():
    """Check if running with admin privileges on Windows"""
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    return True

def run_as_admin():
    """Restart script with admin privileges on Windows"""
    if platform.system() == "Windows":
        import ctypes
        if not is_admin():
            print("🔑 Administrator privileges required for Ollama installation...")
            print("Restarting with admin privileges...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, 
                f'"{__file__}"', None, 1
            )
            sys.exit(0)

def download_file(url, dest_path, description="file"):
    """Download a file with progress indication"""
    print(f"📥 Downloading {description}...")
    
    def progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            percent = (block_num * block_size / total_size) * 100
            print(f"\r   Progress: {percent:.1f}%", end="", flush=True)
    
    try:
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print("\n✅ Download completed")
        return True
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False

def install_ollama_windows():
    """Automatically install Ollama on Windows"""
    print("\n🤖 Installing Ollama for Windows...")
    
    # Try winget first (modern Windows package manager)
    try:
        print("📦 Trying winget installation...")
        result = subprocess.run([
            "winget", "install", "Ollama.Ollama", "--accept-package-agreements", "--accept-source-agreements"
        ], check=True, capture_output=True, text=True)
        print("✅ Ollama installed successfully via winget")
        
        # Wait a moment and verify
        time.sleep(3)
        return verify_ollama_installation()
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📥 winget failed, trying direct download...")
    
    # Fallback to direct download
    with tempfile.TemporaryDirectory() as temp_dir:
        installer_path = Path(temp_dir) / "ollama-installer.exe"
        
        # Download Ollama installer
        ollama_url = "https://ollama.ai/download/OllamaSetup.exe"
        if not download_file(ollama_url, installer_path, "Ollama installer"):
            return False
        
        print("🔧 Running Ollama installer...")
        try:
            # Run installer silently
            result = subprocess.run([
                str(installer_path), 
                "/S",  # Silent install
                "/D=C:\\Program Files\\Ollama"  # Default directory
            ], check=True, capture_output=True, text=True)
            
            print("✅ Ollama installed successfully")
            
            # Add to PATH and refresh environment
            ollama_path = "C:\\Program Files\\Ollama"
            current_path = os.environ.get("PATH", "")
            if ollama_path not in current_path:
                print("🔧 Adding Ollama to PATH...")
                # For current session
                os.environ["PATH"] = f"{ollama_path};{current_path}"
            
            # Refresh environment variables from registry
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                    system_path = winreg.QueryValueEx(key, "PATH")[0]
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                    try:
                        user_path = winreg.QueryValueEx(key, "PATH")[0]
                    except FileNotFoundError:
                        user_path = ""
                
                # Update current session PATH
                full_path = f"{system_path};{user_path}"
                os.environ["PATH"] = full_path
                print("✅ PATH refreshed from registry")
            except Exception as e:
                print(f"⚠️  Could not refresh PATH from registry: {e}")
            
            # Wait a moment for installation to complete
            time.sleep(3)
            
            # Verify installation
            return verify_ollama_installation()
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            print("⚠️  Note: Admin privileges may be required for installation")
            print("   Please run PowerShell as Administrator and try again")
            return False
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            print("⚠️  Note: Admin privileges may be required for installation")
            print("   Please run PowerShell as Administrator and try again")
            return False

def install_ollama_macos():
    """Automatically install Ollama on macOS"""
    print("\n🤖 Installing Ollama for macOS...")
    
    # Try Homebrew first
    try:
        subprocess.run(["brew", "--version"], check=True, capture_output=True)
        print("🍺 Using Homebrew to install Ollama...")
        subprocess.run(["brew", "install", "ollama"], check=True)
        print("✅ Ollama installed via Homebrew")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📥 Homebrew not available, trying direct installation...")
    
    # Try MacPorts
    try:
        subprocess.run(["port", "version"], check=True, capture_output=True)
        print("🚢 Using MacPorts to install Ollama...")
        subprocess.run(["sudo", "port", "install", "ollama"], check=True)
        print("✅ Ollama installed via MacPorts")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📥 MacPorts not available, trying direct download...")
    
    # Fallback to manual installation
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / "ollama-darwin.zip"
        
        # Download Ollama for macOS
        ollama_url = "https://ollama.ai/download/Ollama-darwin.zip"
        if not download_file(ollama_url, zip_path, "Ollama for macOS"):
            return False
        
        print("📦 Extracting Ollama...")
        try:
            # Extract and install
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Move to Applications
            print("🔧 Installing to /Applications...")
            app_path = Path(temp_dir) / "Ollama.app"
            if app_path.exists():
                dest_path = Path("/Applications/Ollama.app")
                if dest_path.exists():
                    subprocess.run(["rm", "-rf", str(dest_path)], check=True)
                subprocess.run(["mv", str(app_path), "/Applications/"], check=True)
                
                # Create CLI symlink
                cli_source = Path("/Applications/Ollama.app/Contents/Resources/ollama")
                cli_dest = Path("/usr/local/bin/ollama")
                cli_dest.parent.mkdir(exist_ok=True)
                if cli_dest.exists():
                    cli_dest.unlink()
                try:
                    cli_dest.symlink_to(cli_source)
                except PermissionError:
                    print("⚠️  Could not create CLI symlink, you may need to add Ollama to PATH manually")
                
                print("✅ Ollama installed to Applications")
                return True
            else:
                print("❌ Ollama.app not found in downloaded archive")
                return False
                
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False

def install_ollama_linux():
    """Automatically install Ollama on Linux"""
    print("\n🤖 Installing Ollama for Linux...")
    
    try:
        # Use the official install script
        print("📥 Downloading and running Ollama install script...")
        result = subprocess.run([
            "curl", "-fsSL", "https://ollama.ai/install.sh"
        ], capture_output=True, text=True, check=True)
        
        # Pipe to sh
        install_process = subprocess.run([
            "sh"
        ], input=result.stdout, text=True, check=True)
        
        print("✅ Ollama installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False

def start_ollama_service():
    """Start Ollama service and wait for it to be ready"""
    print("\n🚀 Starting Ollama service...")
    
    system = platform.system().lower()
    
    # Find the correct Ollama executable
    ollama_cmd = find_ollama_executable()
    if not ollama_cmd:
        print("❌ Could not find Ollama executable")
        return False
    
    try:
        if system == "windows":
            # On Windows, start in a new console window
            subprocess.Popen([
                ollama_cmd, "serve"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # On Unix systems, start in background
            subprocess.Popen([
                ollama_cmd, "serve"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for service to be ready
        print("⏳ Waiting for Ollama service to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama service is ready")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("⚠️  Ollama service may not be fully ready, continuing...")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not start Ollama service: {e}")
        return False

def find_ollama_executable():
    """Find the Ollama executable in various locations"""
    possible_paths = [
        "ollama",  # If in PATH
        "C:\\Program Files\\Ollama\\ollama.exe",
        "C:\\Users\\{}\\AppData\\Local\\Programs\\Ollama\\ollama.exe".format(os.getenv("USERNAME", "")),
        "/usr/local/bin/ollama",
        "/opt/homebrew/bin/ollama", 
        "/Applications/Ollama.app/Contents/Resources/ollama"
    ]
    
    for ollama_path in possible_paths:
        try:
            result = subprocess.run([ollama_path, "--version"], 
                                  capture_output=True, text=True, check=True, timeout=5)
            return ollama_path
        except:
            continue
    
    return None

def download_recommended_models():
    """Download recommended AI models"""
    print("\nAI Model Download (Automatic Setup)...")
    
    # Find the correct Ollama executable
    ollama_cmd = find_ollama_executable()
    if not ollama_cmd:
        print("[ERROR] Could not find Ollama executable")
        return False
    
    # Automatically choose quick setup with small model
    print("\nAutomatically selecting quick setup:")
    print("- Downloading small model (~700MB) for faster setup")
    print("- You can add larger models later if needed")
    
    models = [("llama3.2:1b", "Llama 3.2 1B - Lightweight option (~700MB)")]
    timeout = 300  # 5 minutes
    
    success_count = 0
    for model_name, description in models:
        print(f"\nDownloading {description}...")
        print("   This may take several minutes depending on your internet connection...")
        
        try:
            # Start the download process
            process = subprocess.Popen([
                ollama_cmd, "pull", model_name
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            # Show progress
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Print download progress if available
                    line = output.strip()
                    if any(keyword in line.lower() for keyword in ['pulling', 'downloading', 'verifying', 'writing']):
                        print(f"   {line}")
            
            if process.returncode == 0:
                print(f"[OK] {model_name} downloaded successfully")
                success_count += 1
            else:
                print(f"[ERROR] Failed to download {model_name}")
                
        except Exception as e:
            print(f"[ERROR] Failed to download {model_name}: {e}")
    
    if success_count > 0:
        print(f"\n[OK] Successfully downloaded {success_count}/{len(models)} models")
        print("You're ready to use the AI assistant!")
        return True
    else:
        print("\n[WARNING] No models were downloaded, but you can do this later")
        print(f"   Run: {ollama_cmd} pull llama3.2:1b")
        return False

def install_ollama_automatically():
    """Automatically install Ollama based on the operating system"""
    system = platform.system().lower()
    
    if system == "windows":
        return install_ollama_windows()
    elif system == "darwin":
        return install_ollama_macos()
    elif system == "linux":
        return install_ollama_linux()
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def enhanced_check_ollama():
    """Enhanced Ollama check with automatic installation"""
    print("\n🤖 Checking Ollama status...")
    
    # Check if ollama command exists using verification function
    if not verify_ollama_installation():
        print("❌ Ollama not found")
        print("🚀 Automatically installing Ollama...")
        
        if install_ollama_automatically():
            print("✅ Ollama installation completed, checking status...")
            # Give installation more time to complete
            time.sleep(5)
            if not verify_ollama_installation():
                print("❌ Ollama installation verification failed")
                print("📥 Manual installation options:")
                print("   Windows: https://ollama.ai/download")
                print("   macOS: brew install ollama")
                print("   Linux: curl -fsSL https://ollama.ai/install.sh | sh")
                return "install_failed"
        else:
            print("❌ Automatic installation failed")
            return "install_failed"
    
    # Now check if service is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            
            # Check for models
            models = response.json().get('models', [])
            if models:
                print(f"✅ {len(models)} model(s) available")
                return "ready"
            else:
                print("📥 No models found, will download recommended models")
                return "no_models"
        else:
            print("🚀 Starting Ollama service...")
            if start_ollama_service():
                return "no_models"
            else:
                return "service_failed"
    except Exception as e:
        print(f"🚀 Ollama service not running, starting it... ({e})")
        if start_ollama_service():
            return "no_models"
        else:
            return "service_failed"

def create_enhanced_startup_scripts():
    """Create enhanced startup scripts with Ollama service management"""
    print("\n📜 Creating enhanced startup scripts...")
    
    project_root = Path(__file__).parent
    
    # Enhanced Windows batch file
    if platform.system() == "Windows":
        batch_content = """@echo off
echo Starting On-Device LLM Assistant...
cd /d "%~dp0"

REM Check if Ollama service is running
echo Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Start the application
python launcher.py

pause
"""
        with open(project_root / "start.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print("✅ Created enhanced start.bat")
    
    # Enhanced Unix shell script
    bash_content = """#!/bin/bash
echo "Starting On-Device LLM Assistant..."
cd "$(dirname "$0")"

# Check if Ollama service is running
echo "Checking Ollama service..."
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Activate virtual environment
source venv/bin/activate

# Start the application
python launcher.py
"""
    with open(project_root / "start.sh", "w", encoding="utf-8") as f:
        f.write(bash_content)
    
    # Make shell script executable
    if platform.system() != "Windows":
        os.chmod(project_root / "start.sh", 0o755)
        print("✅ Created enhanced start.sh")

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
    
    # Check npm (improved detection)
    try:
        if platform.system() == "Windows":
            # Try PowerShell npm first
            result = subprocess.run(["powershell", "-Command", "npm --version"], capture_output=True, text=True, check=True)
        else:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        npm_version = result.stdout.strip()
        print(f"✅ npm {npm_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try alternative detection methods
        try:
            result = subprocess.run(["where", "npm"], capture_output=True, text=True, check=True)
            print("✅ npm found")
        except:
            issues.append("npm not found - comes with Node.js")
    
    # Check git
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        git_version = result.stdout.strip()
        print(f"✅ {git_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("Git not found - required for version control")
    
    return issues

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
    
    current_dir = os.getcwd()
    os.chdir(frontend_path)
    
    try:
        # Install npm dependencies
        if (frontend_path / "package.json").exists():
            print("Installing npm dependencies...")
            if platform.system() == "Windows":
                subprocess.run(["powershell", "-Command", "npm install"], check=True)
            else:
                subprocess.run(["npm", "install"], check=True)
            print("✅ npm dependencies installed")
            
            # Build frontend
            print("Building frontend...")
            if platform.system() == "Windows":
                subprocess.run(["powershell", "-Command", "npm run build"], check=True)
            else:
                subprocess.run(["npm", "run", "build"], check=True)
            print("✅ Frontend built successfully")
            
            return True
        else:
            print("❌ package.json not found")
            return False
    finally:
        os.chdir(current_dir)

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
"""

    with open(Path(__file__).parent / "DEVELOPMENT_ENHANCED.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("✅ Created DEVELOPMENT_ENHANCED.md")

def verify_ollama_installation():
    """Verify that Ollama is properly installed and accessible"""
    print("🔍 Verifying Ollama installation...")
    
    # Try different possible locations
    possible_paths = [
        "ollama",  # If in PATH
        "C:\\Program Files\\Ollama\\ollama.exe",
        "C:\\Users\\{}\\AppData\\Local\\Programs\\Ollama\\ollama.exe".format(os.getenv("USERNAME", "")),
        "/usr/local/bin/ollama",
        "/opt/homebrew/bin/ollama",
        "/Applications/Ollama.app/Contents/Resources/ollama"
    ]
    
    for ollama_path in possible_paths:
        try:
            result = subprocess.run([ollama_path, "--version"], 
                                  capture_output=True, text=True, check=True, timeout=10)
            print(f"✅ Found Ollama at: {ollama_path}")
            print(f"   Version: {result.stdout.strip()}")
            
            # Update environment to use this path
            if ollama_path != "ollama":
                ollama_dir = str(Path(ollama_path).parent)
                current_path = os.environ.get("PATH", "")
                if ollama_dir not in current_path:
                    os.environ["PATH"] = f"{ollama_dir};{current_path}"
                    print(f"✅ Added {ollama_dir} to PATH")
            
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    print("❌ Ollama installation could not be verified")
    print("   The installation may have succeeded but Ollama is not in PATH")
    print("   You may need to restart your terminal or add Ollama to PATH manually")
    return False

def main():
    """Enhanced main setup function"""
    print_banner()
    
    # Check for admin privileges on Windows if needed
    if platform.system() == "Windows":
        print("ℹ️  Note: Admin privileges may be required for Ollama installation")
    
    # Check system requirements (now self-contained)
    issues = check_system_requirements()
    if issues:
        print("\n❌ System Requirements Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease resolve these issues and run setup again.")
        return False
    
    # Enhanced Ollama check with auto-installation
    ollama_status = enhanced_check_ollama()
    
    if ollama_status == "install_failed":
        print("\n⚠️  Ollama installation failed, but continuing with setup...")
        print("📥 You can install Ollama manually later:")
        print("   Windows: https://ollama.ai/download")
        print("   macOS: brew install ollama")
        print("   Linux: curl -fsSL https://ollama.ai/install.sh | sh")
    elif ollama_status == "not_installed":
        print("\n⚠️  Continuing without Ollama. You can install it later.")
    elif ollama_status == "no_models":
        download_recommended_models()
    elif ollama_status == "service_failed":
        print("\n⚠️  Ollama installed but service failed to start. You may need to start it manually:")
        print("   ollama serve")
    elif ollama_status == "ready":
        print("✅ Ollama is ready with models available!")
    
    try:
        # Setup Python environment
        python_path, pip_path = setup_python_environment()
        
        # Setup frontend
        current_dir = os.getcwd()
        frontend_success = setup_frontend()
        os.chdir(current_dir)
        
        # Create enhanced startup scripts
        create_enhanced_startup_scripts()
        
        # Create development guide
        create_development_guide()
        
        print("\n" + "="*60)
        print("🎉 Enhanced setup completed successfully!")
        print("="*60)
        print("\n🚀 To start the application:")
        if platform.system() == "Windows":
            print("   Double-click: start.bat")
        else:
            print("   Run: ./start.sh")
        print("   Or: python launcher.py")
        
        print("\n🤖 Ollama Models:")
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
            print(result.stdout)
        except:
            print("   Run 'ollama pull llama3.2:3b' to download models")
        
        # Automatically start the application
        print("\nStarting application automatically...")
        try:
            subprocess.run([sys.executable, "launcher.py"])
        except Exception as e:
            print(f"Failed to start application: {e}")
            print("You can start it manually with: python launcher.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Please check the error above and try again.")
        return False

if __name__ == "__main__":
    main()
