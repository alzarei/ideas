# 🤖 On-Device LLM Assistant

Professional local AI chat application with Victorian prose style training.

## 🏗 Architecture

```
on-device-slm/
├── backend/           # FastAPI server
│   ├── main.py       # API endpoints & server
│   └── fallback.html # Simple status page
├── frontend/         # React TypeScript UI
│   ├── src/          # React components
│   ├── public/       # Static assets
│   └── package.json  # Dependencies
├── examples/         # AI client modules
│   ├── hello_world.py
│   ├── style_training.py
│   └── token_management.py
├── launcher.py       # Application launcher
└── requirements.txt  # Python dependencies
```

## 🚀 Quick Start

### Method 1: One-Click Launch
```bash
python launcher.py
```

### Method 2: Manual Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the backend:**
   ```bash
   cd backend
   python main.py
   ```

3. **Build the frontend** (optional):
   ```bash
   cd frontend
   npm install
   npm run build
   ```

4. **Open browser:** http://localhost:8000

## 🌟 Features

### ✅ Working Now
- **FastAPI Backend** - Professional REST API
- **Health Monitoring** - Real-time system status
- **Demo Mode** - Works without Ollama
- **API Documentation** - Auto-generated at `/api/docs`
- **Token Management** - Context window awareness
- **Cross-Platform** - Windows, Mac, Linux

### 🔧 React Frontend (Ready to Build)
- **Modern TypeScript** - Type-safe development
- **Professional UI** - Clean, responsive design
- **Chat Interface** - Real-time messaging
- **Victorian Style Tab** - Prose generation
- **Status Indicators** - Live health monitoring

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System status & Ollama check |
| `/api/chat` | POST | Chat with local model |
| `/api/style` | POST | Generate Victorian prose |
| `/api/models` | GET | List available models |
| `/api/docs` | GET | Interactive API documentation |

## 🔌 Integration with Ollama

### Prerequisites
1. **Install Ollama:** https://ollama.ai
2. **Download model:** `ollama pull llama3.2:3b`
3. **Start Ollama service**

### Without Ollama
The application runs in **demo mode** with mock responses.

## 🎯 Professional Benefits

### For Hiring Managers
- **Modern Architecture:** FastAPI + React TypeScript
- **Industry Standards:** REST API, OpenAPI docs, CORS
- **Production Patterns:** Health checks, error handling, logging
- **Scalable Design:** Microservices architecture

### For Development
- **Type Safety:** Full TypeScript implementation
- **Hot Reload:** Development server with live updates
- **Testing Ready:** Jest and React Testing Library setup
- **Deployment Ready:** Docker-friendly structure

## 📦 Deployment Options

### Development
```bash
# Backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend (optional)
cd frontend && npm start
```

### Production
```bash
# Build React app
cd frontend && npm run build

# Serve everything from FastAPI
python backend/main.py
```

### Docker (Future)
```dockerfile
# Multi-stage build ready
FROM node:18-alpine AS frontend-build
FROM python:3.11-slim AS backend
```

## 🛠 Development Workflow

1. **Backend Changes:** Edit `backend/main.py` → Auto-reload
2. **Frontend Changes:** Edit `frontend/src/` → Build with `npm run build`
3. **API Testing:** Use `/api/docs` for interactive testing
4. **Health Check:** Visit `/api/health` for status

## 🎨 Customization

### Adding New Endpoints
```python
# In backend/main.py
@app.post("/api/custom")
async def custom_endpoint(request: CustomRequest):
    # Your logic here
    return {"result": "success"}
```

### Styling Frontend
- Edit `frontend/src/App.css` for visual changes
- Modify `frontend/src/App.tsx` for functionality

## 📚 Next Steps

1. **Complete React Setup:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Add Features:**
   - Conversation history
   - Model switching
   - File upload/download
   - Settings panel

3. **Production Deployment:**
   - Add authentication
   - Configure reverse proxy
   - Set up SSL/TLS
   - Add monitoring

## 🤝 Contributing

This architecture supports easy development:
- Backend: Standard FastAPI patterns
- Frontend: Create React App with TypeScript
- API: OpenAPI/Swagger documentation
- Testing: Built-in frameworks

## 📄 License

MIT License - Feel free to use in your projects!

---

**Built with:** FastAPI, React, TypeScript, Ollama
**Architecture:** Modern microservices pattern
**Status:** Production-ready foundation ✨
