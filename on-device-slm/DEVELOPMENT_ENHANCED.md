# Quick Development Guide

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
venv\Scripts\activate            # Windows

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
