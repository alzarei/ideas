#!/usr/bin/env python3
"""
Universal Ollama installer for all platforms
Handles package managers and direct downloads
"""

import subprocess
import sys
import os
import platform
import urllib.request
import tempfile
import zipfile
import tarfile
import shutil
from pathlib import Path

class OllamaInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        
    def detect_package_manager(self):
        """Detect available package managers"""
        managers = {
            'brew': 'brew --version',
            'chocolatey': 'choco --version', 
            'scoop': 'scoop --version',
            'winget': 'winget --version',
            'apt': 'apt --version',
            'yum': 'yum --version',
            'dnf': 'dnf --version',
            'pacman': 'pacman --version',
            'zypper': 'zypper --version'
        }
        
        available = []
        for manager, command in managers.items():
            try:
                subprocess.run(command.split(), capture_output=True, check=True)
                available.append(manager)
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        return available
    
    def install_via_package_manager(self):
        """Try to install via package manager"""
        managers = self.detect_package_manager()
        
        install_commands = {
            'brew': ['brew', 'install', 'ollama'],
            'chocolatey': ['choco', 'install', 'ollama', '-y'],
            'scoop': ['scoop', 'install', 'ollama'],
            'winget': ['winget', 'install', 'Ollama.Ollama'],
            'apt': ['sudo', 'snap', 'install', 'ollama'],
            'yum': ['sudo', 'yum', 'install', '-y', 'ollama'],
            'dnf': ['sudo', 'dnf', 'install', '-y', 'ollama'],
            'pacman': ['sudo', 'pacman', '-S', 'ollama'],
            'zypper': ['sudo', 'zypper', 'install', '-y', 'ollama']
        }
        
        for manager in managers:
            if manager in install_commands:
                print(f"🍺 Installing Ollama via {manager}...")
                try:
                    subprocess.run(install_commands[manager], check=True)
                    print(f"✅ Ollama installed successfully via {manager}")
                    return True
                except subprocess.CalledProcessError:
                    print(f"❌ Failed to install via {manager}")
                    continue
        
        return False
    
    def download_direct_installer(self):
        """Download and install directly from Ollama"""
        if self.system == 'windows':
            return self.install_windows_direct()
        elif self.system == 'darwin':
            return self.install_macos_direct()
        elif self.system == 'linux':
            return self.install_linux_direct()
        else:
            print(f"❌ Unsupported system: {self.system}")
            return False
    
    def install_windows_direct(self):
        """Direct Windows installation"""
        print("📥 Downloading Ollama for Windows...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            installer_path = Path(temp_dir) / "OllamaSetup.exe"
            
            try:
                # Download installer
                url = "https://ollama.ai/download/OllamaSetup.exe"
                self.download_with_progress(url, installer_path)
                
                # Run installer
                print("🔧 Running installer...")
                result = subprocess.run([str(installer_path), '/S'], check=True)
                
                # Add to PATH
                ollama_path = Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / 'Ollama'
                self.add_to_path(str(ollama_path))
                
                print("✅ Ollama installed successfully")
                return True
                
            except Exception as e:
                print(f"❌ Installation failed: {e}")
                return False
    
    def install_macos_direct(self):
        """Direct macOS installation"""
        print("📥 Downloading Ollama for macOS...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "Ollama-darwin.zip"
            
            try:
                # Download
                url = "https://ollama.ai/download/Ollama-darwin.zip"
                self.download_with_progress(url, zip_path)
                
                # Extract
                print("📦 Extracting...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Install to Applications
                app_path = Path(temp_dir) / "Ollama.app"
                if app_path.exists():
                    dest_path = Path("/Applications/Ollama.app")
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.move(str(app_path), str(dest_path))
                    
                    # Add CLI to PATH
                    cli_path = dest_path / "Contents/Resources/ollama"
                    symlink_path = Path("/usr/local/bin/ollama")
                    symlink_path.parent.mkdir(exist_ok=True)
                    if symlink_path.exists():
                        symlink_path.unlink()
                    symlink_path.symlink_to(cli_path)
                    
                    print("✅ Ollama installed successfully")
                    return True
                else:
                    print("❌ Ollama.app not found in download")
                    return False
                    
            except Exception as e:
                print(f"❌ Installation failed: {e}")
                return False
    
    def install_linux_direct(self):
        """Direct Linux installation using official script"""
        print("📥 Installing Ollama for Linux...")
        
        try:
            # Download and run install script
            result = subprocess.run([
                'curl', '-fsSL', 'https://ollama.ai/install.sh'
            ], capture_output=True, text=True, check=True)
            
            # Run the script
            subprocess.run(['sh'], input=result.stdout, text=True, check=True)
            
            print("✅ Ollama installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def download_with_progress(self, url, dest_path):
        """Download file with progress bar"""
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = (block_num * block_size / total_size) * 100
                print(f"\r   Progress: {percent:.1f}%", end="", flush=True)
        
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print()  # New line after progress
    
    def add_to_path(self, new_path):
        """Add directory to system PATH"""
        if self.system == 'windows':
            try:
                # Add to user PATH
                current_path = os.environ.get('PATH', '')
                if new_path not in current_path:
                    os.environ['PATH'] = f"{new_path};{current_path}"
                    
                    # Try to add permanently via registry
                    try:
                        import winreg
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
                        user_path = winreg.QueryValueEx(key, 'PATH')[0]
                        if new_path not in user_path:
                            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, f"{user_path};{new_path}")
                        winreg.CloseKey(key)
                    except Exception:
                        pass  # Registry modification failed, but session PATH is updated
            except Exception:
                pass
    
    def install(self):
        """Main installation method"""
        print(f"🤖 Installing Ollama on {self.system}...")
        
        # Check if already installed
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True, check=True)
            print(f"✅ Ollama already installed: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Try package manager first
        if self.install_via_package_manager():
            return True
        
        # Fall back to direct installation
        print("📦 Package manager installation failed, trying direct download...")
        return self.download_direct_installer()

def main():
    """Main function"""
    print("🤖 Universal Ollama Installer")
    print("=" * 40)
    
    installer = OllamaInstaller()
    
    if installer.install():
        print("\n🎉 Ollama installation completed!")
        print("\nNext steps:")
        print("1. Restart your terminal")
        print("2. Run: ollama serve")
        print("3. Run: ollama pull llama3.2:3b")
        return True
    else:
        print("\n❌ Ollama installation failed")
        print("\nManual installation options:")
        print("- Windows: https://ollama.ai/download")
        print("- macOS: brew install ollama")
        print("- Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
