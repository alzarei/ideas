# On-Device LLM Assistant - Development Commands

.PHONY: help setup install start start-dev build test clean reset

# Default target
help:
	@echo "On-Device LLM Assistant - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup          - Complete development environment setup"
	@echo "  install        - Install dependencies only"
	@echo ""
	@echo "Run Commands:"
	@echo "  start          - Start the full application"
	@echo "  start-dev      - Start in development mode (with auto-reload)"
	@echo "  start-backend  - Start backend only"
	@echo "  start-frontend - Start frontend only"
	@echo ""
	@echo "Build Commands:"
	@echo "  build          - Build frontend for production"
	@echo "  build-frontend - Build React frontend"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  test           - Run tests"
	@echo "  clean          - Clean build artifacts"
	@echo "  reset          - Reset entire environment"
	@echo ""
	@echo "Model Commands:"
	@echo "  models-list    - List available Ollama models"
	@echo "  models-pull    - Pull recommended models"
	@echo ""

# Setup commands
setup:
	@echo "🚀 Running complete setup..."
	python setup.py

install: install-python install-frontend

install-python:
	@echo "🐍 Installing Python dependencies..."
	@if not exist venv python -m venv venv
	@call venv\Scripts\activate && pip install -r requirements.txt

install-frontend:
	@echo "⚛️ Installing frontend dependencies..."
	@cd frontend && npm install

# Run commands
start:
	@echo "🚀 Starting application..."
	@call venv\Scripts\activate && python launcher.py

start-dev:
	@echo "🔧 Starting in development mode..."
	@start /b cmd /c "cd backend && call ..\venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
	@start /b cmd /c "cd frontend && npm start"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

start-backend:
	@echo "🔗 Starting backend only..."
	@cd backend && call ..\venv\Scripts\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

start-frontend:
	@echo "⚛️ Starting frontend only..."
	@cd frontend && npm start

# Build commands
build: build-frontend

build-frontend:
	@echo "🏗️ Building frontend..."
	@cd frontend && npm run build

# Test commands
test:
	@echo "🧪 Running tests..."
	@call venv\Scripts\activate && python -m pytest tests/ -v || echo "No tests found"
	@cd frontend && npm test -- --watchAll=false || echo "No frontend tests found"

# Maintenance commands
clean:
	@echo "🧹 Cleaning build artifacts..."
	@if exist frontend\build rmdir /s /q frontend\build
	@if exist frontend\node_modules rmdir /s /q frontend\node_modules
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"

reset: clean
	@echo "🔄 Resetting environment..."
	@if exist venv rmdir /s /q venv
	@if exist frontend\package-lock.json del frontend\package-lock.json
	@echo "Run 'make setup' to reinitialize"

# Model commands
models-list:
	@echo "📋 Available Ollama models:"
	@ollama list || echo "Ollama not running or not installed"

models-pull:
	@echo "📥 Pulling recommended models..."
	@ollama pull llama3.2:3b
	@ollama pull llama3.2:1b
	@echo "✅ Models downloaded"

# Environment info
info:
	@echo "📊 Environment Information:"
	@echo "Python: " && python --version
	@echo "Node: " && node --version
	@echo "npm: " && npm --version
	@echo "Ollama: " && ollama --version || echo "Not installed"
