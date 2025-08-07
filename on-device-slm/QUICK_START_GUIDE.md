# On-Device LLM Assistant - One-Click Setup Guide

## **Quick Start (30 seconds)**

### Option 1: Ultimate One-Click Setup (Recommended)
```powershell
powershell -ExecutionPolicy Bypass -File "one_click_setup.ps1"
```
**This does EVERYTHING:** Installs Python, Node.js, Ollama, sets up the project, and starts the app!

### Option 2: Simple Startup (If already set up)
```batch
start_app.bat
```
**Double-click this file** to instantly start both frontend and backend servers.

---

## **What Each Script Does**

### **one_click_setup.ps1** - The Ultimate Setup
- ✅ Automatically installs Python if missing
- ✅ Automatically installs Node.js if missing  
- ✅ Automatically installs Ollama if missing
- ✅ Sets up Python virtual environment
- ✅ Installs all dependencies
- ✅ Configures the entire project
- ✅ **NO user input required!**

### **start_app.bat** - Instant Startup
- ✅ Starts backend server (Python/FastAPI)
- ✅ Starts frontend server (React)
- ✅ Opens both services simultaneously
- ✅ **Just double-click to run!**

### 🛠️ **dev_enhanced_fixed.ps1** - Advanced Commands
- ✅ Multiple development commands
- ✅ Individual component control
- ✅ Model management
- ✅ Build and deployment tools

---

## 🎮 **Usage Instructions**

### For New Users (First Time Setup):
1. **Right-click** on `one_click_setup.ps1`
2. Select **"Run with PowerShell"**
3. Wait for setup to complete (2-5 minutes)
4. **Done!** The app will start automatically

### For Daily Use:
1. **Double-click** `start_app.bat`
2. Wait 10-15 seconds for services to start
3. **Frontend:** http://localhost:3000
4. **Backend API:** http://localhost:8000

---

## 🔧 **Available Commands**

### Quick Commands:
```powershell
# Show all available commands
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" help

# Check system status
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" info

# Install dependencies only
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" install

# Start full application
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" start

# Start only backend
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" start-backend

# Start only frontend
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" start-frontend
```

### Model Management:
```powershell
# List installed AI models
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" models-list

# Download recommended models
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" models-pull

# Start Ollama service
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" models-serve
```

---

## 🚨 **Troubleshooting**

### If PowerShell blocks execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### If setup fails:
1. Run as Administrator (right-click → "Run as Administrator")
2. Check internet connection
3. Restart terminal and try again

### If services don't start:
```powershell
# Kill any running processes
taskkill /f /im python.exe /im node.exe 2>nul

# Then restart
.\start_app.bat
```

---

## 📂 **File Structure**
```
📁 Project Root
├── 🚀 one_click_setup.ps1    # Ultimate setup script
├── ⚡ start_app.bat               # Quick startup
├── 🛠️ dev_enhanced_fixed.ps1       # Advanced commands
├── 📁 frontend/                    # React app
├── 📁 backend/                     # Python API
├── 📁 config/                      # AI model configs
└── 📄 requirements.txt             # Python dependencies
```

---

## 🎉 **Success Indicators**

When everything works, you'll see:
- ✅ **Frontend:** React development server at http://localhost:3000
- ✅ **Backend:** FastAPI server at http://localhost:8000  
- ✅ **Ollama:** AI model service running
- ✅ **Models:** Pre-configured AI models available

---

## 💡 **Pro Tips**

1. **First time?** Use `one_click_setup.ps1` - it does everything
2. **Daily use?** Just double-click `start_app.bat`
3. **Development?** Use `dev_enhanced_fixed.ps1` commands
4. **Problems?** Check the troubleshooting section above

**This setup takes care of everything automatically - no technical knowledge required!** 🎯
