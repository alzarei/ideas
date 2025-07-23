# 🚀 Quick Start Guide

Get the On-Device LLM Assistant running in under 5 minutes!

## 📋 Prerequisites (Install These First)

### Required Software
1. **Python 3.8+** - [Download](https://python.org/downloads/)
2. **Node.js 16+** - [Download](https://nodejs.org/)
3. **Ollama** - [Download](https://ollama.ai/download)

### Quick Verification
```bash
python --version    # Should show 3.8+
node --version      # Should show 16+
ollama --version    # Should show ollama version
```

## ⚡ Super Quick Start (1 Command)

### Windows
```cmd
python setup.py
```

### Mac/Linux
```bash
python3 setup.py
```

That's it! The setup script will:
- ✅ Create virtual environment
- ✅ Install all dependencies  
- ✅ Build the frontend
- ✅ Download AI models
- ✅ Create startup scripts
- ✅ Launch the application

## 🎮 Start the Application

### Option 1: Startup Scripts (Easiest)
**Windows:** Double-click `start.bat`  
**Mac/Linux:** Run `./start.sh`

### Option 2: Development Scripts
```powershell
# Windows PowerShell
.\dev.ps1 start
```

```bash
# Mac/Linux (if you have Make)
make start
```

### Option 3: Direct Launch
```bash
python launcher.py
```

## 🌐 Access the Application

Once started, open your browser to:
- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## 🎯 For Developers

### Development Mode (Hot Reload)
```powershell
# Windows
.\dev.ps1 start-dev
```

```bash
# Mac/Linux  
make start-dev
```

This starts:
- Backend at http://localhost:8000 (with auto-reload)
- Frontend at http://localhost:3000 (with hot reload)

### Quick Commands
```powershell
# Windows PowerShell
.\dev.ps1 help          # Show all commands
.\dev.ps1 build         # Build for production
.\dev.ps1 test          # Run tests
.\dev.ps1 clean         # Clean build files
```

```bash
# Mac/Linux with Make
make help               # Show all commands
make build              # Build for production  
make test               # Run tests
make clean              # Clean build files
```

## 🔧 Manual Setup (If Automated Fails)

### 1. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate     # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. AI Models Setup
```bash
# Start Ollama service
ollama serve

# Download a model (in another terminal)
ollama pull llama3.2:3b
```

### 4. Start Application
```bash
python launcher.py
```

## 🆘 Troubleshooting

### Problem: "Python not found"
**Solution**: Install Python from https://python.org

### Problem: "Node not found"  
**Solution**: Install Node.js from https://nodejs.org

### Problem: "Ollama not found"
**Solution**: Install Ollama from https://ollama.ai

### Problem: "Dependencies failed to install"
**Solution**: Try manual setup above

### Problem: "Port 8000 already in use"
**Solution**: Stop other services or edit `launcher.py` to use different port

### Problem: "Frontend not loading"
**Solution**: 
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## ✅ Verify Everything Works

Run the verification script:
```bash
python verify.py
```

This checks:
- ✅ Python environment
- ✅ Node.js environment  
- ✅ Ollama installation
- ✅ Project structure
- ✅ Dependencies

## 🚀 What's Next?

1. **Explore the Interface** - Try the conversation features
2. **Switch Models** - Test different AI models in the interface
3. **Read the Docs** - Check out `DEVELOPMENT.md` for advanced features
4. **Customize** - Modify `config/models.json` to add your own models

## 💡 Pro Tips

- Use `python verify.py` to check if everything is working
- The setup script can be run multiple times safely
- All data is stored locally - your conversations are private
- Add new models by editing `config/models.json`
- Development mode automatically reloads when you change code

## 🆘 Still Having Issues?

1. Run `python verify.py` to diagnose problems
2. Check the terminal output for error messages
3. Make sure all prerequisites are installed
4. Try the manual setup steps above
5. Check `DEVELOPMENT.md` for detailed troubleshooting

---

**Ready to build amazing AI applications? Let's go! 🚀**
