#!/usr/bin/env python3
"""
Universal installer for On-Device LLM Assistant
Works with various package managers and operating systems
"""

import subprocess
import sys
import os
import platform
import shutil
from pathlib import Path

def run_command(cmd, shell=False, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=shell, cwd=cwd, capture_output=True, text=True, check=True)
        return True, result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return False, str(e)

def check_command(cmd):
    """Check if a command exists"""
    return shutil.which(cmd) is not None

def install_with_package_manager():
    """Try to install using various package managers"""
    system = platform.system().lower()
    
    if system == "windows":
        # Windows package managers
        if check_command("winget"):
            print("📦 Using Windows Package Manager (winget)...")
            commands = [
                ["winget", "install", "Python.Python.3.11"],
                ["winget", "install", "OpenJS.NodeJS"],
                ["winget", "install", "Ollama.Ollama"]
            ]
        elif check_command("choco"):
            print("📦 Using Chocolatey...")
            commands = [
                ["choco", "install", "python", "-y"],
                ["choco", "install", "nodejs", "-y"],
                ["choco", "install", "ollama", "-y"]
            ]
        elif check_command("scoop"):
            print("📦 Using Scoop...")
            commands = [
                ["scoop", "install", "python"],
                ["scoop", "install", "nodejs"],
                ["scoop", "install", "ollama"]
            ]
        else:
            return False, "No Windows package manager found (winget, choco, scoop)"
            
    elif system == "darwin":
        # macOS package managers
        if check_command("brew"):
            print("📦 Using Homebrew...")
            commands = [
                ["brew", "install", "python@3.11"],
                ["brew", "install", "node"],
                ["brew", "install", "ollama"]
            ]
        elif check_command("port"):
            print("📦 Using MacPorts...")
            commands = [
                ["sudo", "port", "install", "python311"],
                ["sudo", "port", "install", "nodejs18"],
                # Ollama not available in MacPorts
            ]
        else:
            return False, "No macOS package manager found (brew, port)"
            
    else:
        # Linux package managers
        if check_command("apt"):
            print("📦 Using APT (Debian/Ubuntu)...")
            commands = [
                ["sudo", "apt", "update"],
                ["sudo", "apt", "install", "-y", "python3", "python3-pip", "python3-venv"],
                ["sudo", "apt", "install", "-y", "nodejs", "npm"],
            ]
        elif check_command("yum"):
            print("📦 Using YUM (Red Hat/CentOS)...")
            commands = [
                ["sudo", "yum", "install", "-y", "python3", "python3-pip"],
                ["sudo", "yum", "install", "-y", "nodejs", "npm"],
            ]
        elif check_command("dnf"):
            print("📦 Using DNF (Fedora)...")
            commands = [
                ["sudo", "dnf", "install", "-y", "python3", "python3-pip"],
                ["sudo", "dnf", "install", "-y", "nodejs", "npm"],
            ]
        elif check_command("pacman"):
            print("📦 Using Pacman (Arch Linux)...")
            commands = [
                ["sudo", "pacman", "-S", "--noconfirm", "python", "python-pip"],
                ["sudo", "pacman", "-S", "--noconfirm", "nodejs", "npm"],
            ]
        elif check_command("zypper"):
            print("📦 Using Zypper (openSUSE)...")
            commands = [
                ["sudo", "zypper", "install", "-y", "python3", "python3-pip"],
                ["sudo", "zypper", "install", "-y", "nodejs18", "npm18"],
            ]
        else:
            return False, "No Linux package manager found"
    
    # Execute commands
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        success, output = run_command(cmd)
        if not success:
            print(f"⚠️  Command failed: {' '.join(cmd)}")
            print(f"Error: {output}")
    
    return True, "Package manager installation attempted"

def install_ollama_manual():
    """Install Ollama manually if not available via package manager"""
    system = platform.system().lower()
    
    print("\n📥 Installing Ollama manually...")
    
    if system == "linux":
        print("Running Ollama installation script...")
        success, output = run_command(["curl", "-fsSL", "https://ollama.ai/install.sh"], shell=True)
        if success:
            subprocess.run(["sh"], input=output, text=True)
        else:
            print("Failed to download Ollama installation script")
            print("Please install manually from: https://ollama.ai")
    else:
        print(f"Please install Ollama manually from: https://ollama.ai/download")
        if system == "darwin":
            print("Or use: brew install ollama")
        elif system == "windows":
            print("Or use: winget install Ollama.Ollama")

def main():
    """Main installation function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Universal Installer for                        ║
║            On-Device LLM Assistant                          ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    print(f"🖥️  Detected OS: {platform.system()} {platform.release()}")
    
    # Check if already installed
    if all(check_command(cmd) for cmd in ["python3", "node", "ollama"]) or all(check_command(cmd) for cmd in ["python", "node", "ollama"]):
        print("✅ All dependencies appear to be installed!")
        print("Running project setup...")
        success, output = run_command([sys.executable, "setup.py"])
        if success:
            print("🎉 Installation completed successfully!")
        else:
            print("❌ Project setup failed. Please check the output above.")
        return
    
    # Try package manager installation
    print("\n🔍 Checking for package managers...")
    success, message = install_with_package_manager()
    
    if not success:
        print(f"⚠️  {message}")
        print("\n📖 Manual installation required:")
        print("1. Python 3.8+: https://python.org/downloads/")
        print("2. Node.js 16+: https://nodejs.org/")
        print("3. Ollama: https://ollama.ai/download")
        return
    
    # Install Ollama manually if needed
    if not check_command("ollama"):
        install_ollama_manual()
    
    # Verify installation
    print("\n🔍 Verifying installation...")
    all_good = True
    
    for cmd, name in [("python3", "Python"), ("python", "Python"), ("node", "Node.js"), ("ollama", "Ollama")]:
        if check_command(cmd):
            success, version = run_command([cmd, "--version"])
            if success:
                print(f"✅ {name}: {version.strip()}")
            else:
                print(f"✅ {name}: installed")
        else:
            if cmd == "python3" and check_command("python"):
                continue  # Skip if python3 not found but python is
            print(f"❌ {name}: not found")
            all_good = False
    
    if all_good:
        print("\n🚀 Running project setup...")
        success, output = run_command([sys.executable, "setup.py"])
        if success:
            print("\n🎉 Installation completed successfully!")
            print("Run 'python launcher.py' to start the application")
        else:
            print("\n❌ Project setup failed:")
            print(output)
    else:
        print("\n❌ Some dependencies are missing.")
        print("Please install them manually and run 'python setup.py'")

if __name__ == "__main__":
    main()
