# On-Device LLM Assistant

A complete solution for running Large Language Models locally with a beautiful web interface.

## Quick Start

**Option 1: Complete First-Time Setup**
**Does everything automatically - perfect for new users!**
```powershell
powershell -ExecutionPolicy Bypass -File "one_click_setup.ps1"
```
- Installs Python, Node.js, Ollama automatically
- Sets up entire project 
- Starts the application
- **No user input required!**

### ⚡ **start_app.bat** - Daily Startup
**Quick startup for daily use - just double-click!**
```batch
start_app.bat
```n for running small language models locally with an intuitive web interface. Features conversation management, model switching, and intelligent system analysis capabilities.

## **ONE-CLICK SETUP** (30 seconds)

### **Ultimate Easy Setup - Just Double-Click!**

**Option 1: Complete First-Time Setup**
1. **Double-click:** `setup.bat`
2. **Wait 2-3 minutes** for automatic installation
3. **Done!** Your AI assistant opens in the browser

**Option 2: Daily Quick Start** (after setup)
1. **Double-click:** `start_app.bat` 
2. **Wait 15 seconds** for services to start
3. **Chat interface opens automatically!**

### 🌐 **Access Your AI Assistant:**
- **Chat Interface:** http://localhost:3000
- **API Server:** http://localhost:8000

### 🎁 **What You Get:**
- 🤖 **Private AI Chat** - Talk to AI models running on your computer
- 💬 **Conversation History** - All chats saved locally
- 🔄 **Multiple AI Models** - Switch between different AI personalities  
- 🔒 **100% Private** - No internet required, no data shared
- 🖥️ **Simple Interface** - Just type and chat like any messaging app

**💡 That's it! No technical knowledge required - everything is automated!**

---

## �️ **Available Scripts**

### � **one_click_setup_fixed.ps1** - Ultimate Setup
**Does everything automatically - perfect for new users!**
```powershell
powershell -ExecutionPolicy Bypass -File "one_click_setup_fixed.ps1"
```
- Installs Python, Node.js, Ollama automatically
- Sets up entire project 
- Starts the application
- **No user input required!**

### ⚡ **start_both.bat** - Daily Startup
**Quick startup for daily use - just double-click!**
```batch
start_both.bat
```
- Starts both frontend and backend
- Opens in seconds
- Perfect for regular use

### 🛠️ **dev_enhanced_fixed.ps1** - Developer Commands
**Advanced control for developers:**
```powershell
# Show all commands
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" help

# Individual controls
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" start-backend
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" start-frontend
powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" models-list
```

---

## 🧑‍💻 For Developers

**📚 Quick Links:**
- [Quick Start Guide](QUICK_START_GUIDE.md) - Complete setup instructions
- [Development Guide](DEVELOPMENT.md) - Detailed development workflow
- [Architecture Guide](ARCHITECTURE.md) - System overview
.\dev.ps1 start         # Start application
.\dev.ps1 start-dev     # Development mode
.\dev.ps1 help          # See all commands
```

**Unix/Linux/macOS:**
```bash
make start              # Start application  
make start-dev          # Development mode
make help               # See all commands
```

## 🏗️ Project Structure

```
├── backend/              # FastAPI backend server
│   ├── main.py          # Main API server
│   ├── conversation_manager.py  # Chat state management
│   └── fallback.html    # Fallback UI
├── frontend/            # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   └── hooks/       # Custom hooks
│   └── build/           # Production build
├── config/              # Configuration files
│   ├── models.json      # Available LLM models
│   ├── model_manager.py # Model management
│   └── training_config.py
├── examples/            # Usage examples
├── writing_samples/     # Training samples
├── setup.py            # Automated setup script
├── launcher.py         # Application launcher
├── dev.ps1             # PowerShell dev script
└── Makefile            # Make development tasks
```

## 🚀 Features

### Core Functionality
- **Conversation Management**: Persistent chat history with context switching
- **Multiple Models**: Support for various Ollama models with easy switching
- **Web Interface**: Modern React frontend with real-time updates
- **Local Processing**: Complete privacy with on-device inference
- **Token Management**: Smart context window handling and conversation trimming

### Models Included
- **Llama 3.2 3B/1B** - Balanced performance and efficiency
- **Dolphin Llama3 8B** - Enhanced reasoning capabilities  
- **Code Llama** - Specialized for code analysis
- **Gemma 2B** - Lightweight option
- **Phi-3 Mini** - Microsoft's efficient model
- **Wizard Vicuna** - Uncensored creative model

### Development Features
- **Hot Reload**: Automatic restart on code changes
- **API Documentation**: Built-in Swagger/OpenAPI docs
- **Health Monitoring**: System status endpoints
- **Modular Architecture**: Easy to extend and customize

## 📚 Usage

### Starting the Application
```bash
# Quick start (automated)
python launcher.py

# Development mode (hot reload)
.\dev.ps1 start-dev      # Windows
make start-dev           # Unix/Linux/macOS
```

### Accessing the Interface
- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs  
- **Health Check**: http://localhost:8000/api/health
- **Frontend Only**: http://localhost:3000 (dev mode)

### Managing Models
```bash
# List available models
ollama list

# Pull new models
ollama pull llama3.2:3b
ollama pull dolphin-llama3:8b

# Configure models in config/models.json
```

## 🛠️ Development

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Ollama** ([Download](https://ollama.ai))
- **Git** for version control

### Development Workflow
```bash
# Full development setup
python setup.py

# Start backend only
.\dev.ps1 start-backend  # Windows
make start-backend       # Unix/Linux/macOS

# Start frontend only  
.\dev.ps1 start-frontend # Windows
make start-frontend      # Unix/Linux/macOS

# Run tests
.\dev.ps1 test          # Windows
make test               # Unix/Linux/macOS

# Clean build artifacts
.\dev.ps1 clean         # Windows
make clean              # Unix/Linux/macOS
```

### Adding New Models
1. Edit `config/models.json`
2. Add model configuration:
```json
{
  "id": "new-model:7b",
  "name": "New Model 7B", 
  "description": "Description of capabilities",
  "category": "general",
  "size_gb": 4.1,
  "context_window": 4096,
  "install_command": "ollama pull new-model:7b",
  "enabled": true
}
```
3. Pull the model: `ollama pull new-model:7b`
4. Restart the application

## 📋 Available Commands

### PowerShell (Windows)
```powershell
.\dev.ps1 help          # Show all commands
.\dev.ps1 setup         # Complete setup
.\dev.ps1 start         # Start application
.\dev.ps1 start-dev     # Development mode
.\dev.ps1 build         # Build for production
.\dev.ps1 test          # Run tests
.\dev.ps1 clean         # Clean artifacts
.\dev.ps1 reset         # Reset environment
.\dev.ps1 models-list   # List Ollama models
.\dev.ps1 models-pull   # Download recommended models
```

### Make (Unix/Linux/macOS)
```bash
make help               # Show all commands
make setup              # Complete setup  
make start              # Start application
make start-dev          # Development mode
make build              # Build for production
make test               # Run tests
make clean              # Clean artifacts
make reset              # Reset environment
make models-list        # List Ollama models
make models-pull        # Download recommended models
```

## 🔧 Configuration

### Environment Setup
The setup process automatically:
- Creates Python virtual environment
- Installs all dependencies
- Downloads recommended models
- Builds the frontend
- Creates startup scripts
- Generates development guide

### Manual Configuration
- **Models**: Edit `config/models.json`
- **Training**: Modify `config/training_config.py`
- **Backend**: Configure in `backend/main.py`
- **Frontend**: Customize in `frontend/src/`

## 🚀 Production Deployment

```bash
# Build for production
.\dev.ps1 build         # Windows
make build              # Unix/Linux/macOS

# The frontend will be built to frontend/build/
# Backend serves static files automatically
```

## 🐛 Troubleshooting

### Common Issues

**Ollama not found:**
```bash
# Install Ollama
# Windows: Download from https://ollama.ai
# macOS: brew install ollama  
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**Python virtual environment issues:**
```bash
.\dev.ps1 reset         # Reset everything
.\dev.ps1 setup         # Rebuild environment
```

## 📚 Documentation

### For Users
- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete guide for non-technical users
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide

### For Developers  
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Detailed development workflow
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture overview
- **[STYLE_TRAINING_GUIDE.md](STYLE_TRAINING_GUIDE.md)** - Model training guidelines
- **[TOKEN_LIMITS_GUIDE.md](TOKEN_LIMITS_GUIDE.md)** - Context management

### Setup Verification
- Run `python verify.py` to check installation status
- Check `examples/` directory for usage samples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and test: `.\dev.ps1 test`
4. Commit changes: `git commit -am 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

**Frontend build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Port conflicts:**
- Backend: Change port in `launcher.py` (default: 8000)
- Frontend dev: Change in `frontend/package.json` (default: 3000)

### Getting Help
1. Check `DEVELOPMENT.md` for detailed guides
2. View API docs at http://localhost:8000/api/docs
3. Examine logs in the terminal output
4. Verify Ollama status: `ollama list`

## 📖 Additional Documentation

- **DEVELOPMENT.md** - Detailed development guide
- **ARCHITECTURE.md** - System architecture overview
- **STYLE_TRAINING_GUIDE.md** - Model training guidelines
- **TOKEN_LIMITS_GUIDE.md** - Context management strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and test: `.\dev.ps1 test`
4. Commit changes: `git commit -am 'Add new feature'`
5. Push to branch: `git push origin feature/new-feature`
6. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
