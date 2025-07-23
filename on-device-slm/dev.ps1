# On-Device LLM Assistant - PowerShell Development Script
# Usage: .\dev.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "On-Device LLM Assistant - Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup Commands:" -ForegroundColor Yellow
    Write-Host "  setup          - Complete development environment setup"
    Write-Host "  install        - Install dependencies only"
    Write-Host ""
    Write-Host "Run Commands:" -ForegroundColor Yellow
    Write-Host "  start          - Start the full application"
    Write-Host "  start-dev      - Start in development mode (with auto-reload)"
    Write-Host "  start-backend  - Start backend only"
    Write-Host "  start-frontend - Start frontend only"
    Write-Host ""
    Write-Host "Build Commands:" -ForegroundColor Yellow
    Write-Host "  build          - Build frontend for production"
    Write-Host ""
    Write-Host "Maintenance Commands:" -ForegroundColor Yellow
    Write-Host "  test           - Run tests"
    Write-Host "  clean          - Clean build artifacts"
    Write-Host "  reset          - Reset entire environment"
    Write-Host ""
    Write-Host "Model Commands:" -ForegroundColor Yellow
    Write-Host "  models-list    - List available Ollama models"
    Write-Host "  models-pull    - Pull recommended models"
    Write-Host ""
    Write-Host "Usage: .\dev.ps1 <command>" -ForegroundColor Green
}

function Setup-Environment {
    Write-Host "🚀 Running complete setup..." -ForegroundColor Green
    python setup.py
}

function Install-Dependencies {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Green
    Install-PythonDeps
    Install-FrontendDeps
}

function Install-PythonDeps {
    Write-Host "🐍 Installing Python dependencies..." -ForegroundColor Blue
    
    if (-not (Test-Path "venv")) {
        Write-Host "Creating virtual environment..."
        python -m venv venv
    }
    
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    deactivate
}

function Install-FrontendDeps {
    Write-Host "⚛️ Installing frontend dependencies..." -ForegroundColor Blue
    
    if (Test-Path "frontend") {
        Set-Location frontend
        npm install
        Set-Location ..
    }
}

function Start-Application {
    Write-Host "🚀 Starting application..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
    python launcher.py
    deactivate
}

function Start-Development {
    Write-Host "🔧 Starting in development mode..." -ForegroundColor Green
    
    # Start backend in background
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        Set-Location backend
        & ..\venv\Scripts\Activate.ps1
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        deactivate
    }
    
    # Start frontend in background
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        Set-Location frontend
        npm start
    }
    
    Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow
    
    try {
        Wait-Job $backendJob, $frontendJob
    }
    finally {
        Stop-Job $backendJob, $frontendJob -Force
        Remove-Job $backendJob, $frontendJob -Force
    }
}

function Start-Backend {
    Write-Host "🔗 Starting backend only..." -ForegroundColor Green
    Set-Location backend
    & ..\venv\Scripts\Activate.ps1
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    deactivate
    Set-Location ..
}

function Start-Frontend {
    Write-Host "⚛️ Starting frontend only..." -ForegroundColor Green
    Set-Location frontend
    npm start
    Set-Location ..
}

function Build-Project {
    Write-Host "🏗️ Building project..." -ForegroundColor Green
    Build-Frontend
}

function Build-Frontend {
    Write-Host "🏗️ Building frontend..." -ForegroundColor Blue
    if (Test-Path "frontend") {
        Set-Location frontend
        npm run build
        Set-Location ..
    }
}

function Test-Project {
    Write-Host "🧪 Running tests..." -ForegroundColor Green
    
    # Python tests
    & .\venv\Scripts\Activate.ps1
    if (Test-Path "tests") {
        python -m pytest tests/ -v
    } else {
        Write-Host "No Python tests found" -ForegroundColor Yellow
    }
    deactivate
    
    # Frontend tests
    if (Test-Path "frontend") {
        Set-Location frontend
        npm test -- --watchAll=false
        Set-Location ..
    }
}

function Clean-Project {
    Write-Host "🧹 Cleaning build artifacts..." -ForegroundColor Green
    
    # Clean frontend build
    if (Test-Path "frontend\build") {
        Remove-Item "frontend\build" -Recurse -Force
    }
    
    # Clean Python cache
    Get-ChildItem -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
}

function Reset-Environment {
    Write-Host "🔄 Resetting environment..." -ForegroundColor Red
    Clean-Project
    
    if (Test-Path "venv") {
        Remove-Item "venv" -Recurse -Force
    }
    
    if (Test-Path "frontend\node_modules") {
        Remove-Item "frontend\node_modules" -Recurse -Force
    }
    
    if (Test-Path "frontend\package-lock.json") {
        Remove-Item "frontend\package-lock.json"
    }
    
    Write-Host "Run '.\dev.ps1 setup' to reinitialize" -ForegroundColor Yellow
}

function List-Models {
    Write-Host "📋 Available Ollama models:" -ForegroundColor Green
    try {
        ollama list
    }
    catch {
        Write-Host "Ollama not running or not installed" -ForegroundColor Red
    }
}

function Pull-Models {
    Write-Host "📥 Pulling recommended models..." -ForegroundColor Green
    try {
        ollama pull llama3.2:3b
        ollama pull llama3.2:1b
        Write-Host "✅ Models downloaded" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to download models. Is Ollama running?" -ForegroundColor Red
    }
}

function Show-Info {
    Write-Host "📊 Environment Information:" -ForegroundColor Cyan
    Write-Host "Python: $(python --version 2>&1)"
    Write-Host "Node: $(node --version 2>&1)"
    Write-Host "npm: $(npm --version 2>&1)"
    try {
        Write-Host "Ollama: $(ollama --version 2>&1)"
    }
    catch {
        Write-Host "Ollama: Not installed"
    }
}

# Command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "setup" { Setup-Environment }
    "install" { Install-Dependencies }
    "start" { Start-Application }
    "start-dev" { Start-Development }
    "start-backend" { Start-Backend }
    "start-frontend" { Start-Frontend }
    "build" { Build-Project }
    "test" { Test-Project }
    "clean" { Clean-Project }
    "reset" { Reset-Environment }
    "models-list" { List-Models }
    "models-pull" { Pull-Models }
    "info" { Show-Info }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
