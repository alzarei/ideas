# Enhanced On-Device LLM Assistant - PowerShell Development Script
# Usage: .\dev_enhanced.ps1 <command>

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [switch]$Force,
    [switch]$AdminRequired
)

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Restart script with admin privileges
function Restart-AsAdmin {
    if (-not (Test-Administrator)) {
        Write-Host "🔑 Administrator privileges required for Ollama installation..." -ForegroundColor Yellow
        Write-Host "Restarting with admin privileges..." -ForegroundColor Yellow
        
        $arguments = "-File `"$($MyInvocation.ScriptName)`" $Command"
        Start-Process PowerShell -Verb RunAs -ArgumentList $arguments
        exit
    }
}

function Show-Help {
    Write-Host "Enhanced On-Device LLM Assistant - Available Commands:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup Commands:" -ForegroundColor Yellow
    Write-Host "  setup          - Complete automated setup (including Ollama)"
    Write-Host "  setup-ollama   - Install Ollama automatically"
    Write-Host "  install        - Install dependencies only"
    Write-Host ""
    Write-Host "Run Commands:" -ForegroundColor Yellow
    Write-Host "  start          - Start the full application"
    Write-Host "  start-dev      - Start in development mode"
    Write-Host "  start-backend  - Start backend only"
    Write-Host "  start-frontend - Start frontend only"
    Write-Host ""
    Write-Host "Model Commands:" -ForegroundColor Yellow
    Write-Host "  models-list    - List available Ollama models"
    Write-Host "  models-pull    - Pull recommended models"
    Write-Host "  models-serve   - Start Ollama service"
    Write-Host ""
    Write-Host "Maintenance Commands:" -ForegroundColor Yellow
    Write-Host "  build          - Build frontend for production"
    Write-Host "  test           - Run tests"
    Write-Host "  clean          - Clean build artifacts"
    Write-Host "  reset          - Reset entire environment"
    Write-Host ""
    Write-Host "Flags:" -ForegroundColor Green
    Write-Host "  -Force         - Force reinstallation"
    Write-Host ""
    Write-Host "Usage: .\dev_enhanced.ps1 <command> [-Force]" -ForegroundColor Green
}

function Install-OllamaWindows {
    Write-Host "🤖 Installing Ollama for Windows..." -ForegroundColor Green
    
    # Check if already installed
    try {
        $version = ollama --version 2>$null
        if ($version -and -not $Force) {
            Write-Host "✅ Ollama already installed: $version" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Not installed, continue
    }
    
    # Create temp directory
    $tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
    $installerPath = Join-Path $tempDir "OllamaSetup.exe"
    
    try {
        Write-Host "📥 Downloading Ollama installer..." -ForegroundColor Blue
        
        # Download with progress
        $url = "https://ollama.ai/download/OllamaSetup.exe"
        $webClient = New-Object System.Net.WebClient
        
        Register-ObjectEvent $webClient DownloadProgressChanged -Action {
            $Global:Progress = $Event.SourceEventArgs.ProgressPercentage
            Write-Progress -Activity "Downloading Ollama" -Status "Progress: $Global:Progress%" -PercentComplete $Global:Progress
        } | Out-Null
        
        $webClient.DownloadFile($url, $installerPath)
        $webClient.Dispose()
        Write-Progress -Activity "Downloading Ollama" -Completed
        
        Write-Host "✅ Download completed" -ForegroundColor Green
        
        # Run installer silently
        Write-Host "🔧 Installing Ollama..." -ForegroundColor Blue
        $process = Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Host "✅ Ollama installed successfully" -ForegroundColor Green
            
            # Add to PATH for current session
            $ollamaPath = "${env:ProgramFiles}\Ollama"
            if ($env:PATH -notlike "*$ollamaPath*") {
                $env:PATH += ";$ollamaPath"
            }
            
            # Refresh environment variables
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
            
            return $true
        }
        else {
            Write-Host "❌ Installation failed with exit code: $($process.ExitCode)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        # Cleanup
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force
        }
    }
}

function Start-OllamaService {
    Write-Host "🚀 Starting Ollama service..." -ForegroundColor Green
    
    # Check if already running
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction SilentlyContinue
        Write-Host "✅ Ollama service is already running" -ForegroundColor Green
        return $true
    }
    catch {
        # Not running, start it
    }
    
    try {
        # Start Ollama service in background
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        
        # Wait for service to be ready
        Write-Host "⏳ Waiting for Ollama service to start..." -ForegroundColor Blue
        $timeout = 30
        $elapsed = 0
        
        while ($elapsed -lt $timeout) {
            try {
                $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
                Write-Host "✅ Ollama service is ready" -ForegroundColor Green
                return $true
            }
            catch {
                Start-Sleep -Seconds 1
                $elapsed++
            }
        }
        
        Write-Host "⚠️  Ollama service may not be fully ready, continuing..." -ForegroundColor Yellow
        return $true
    }
    catch {
        Write-Host "❌ Failed to start Ollama service: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Install-RecommendedModels {
    Write-Host "📥 Installing recommended AI models..." -ForegroundColor Green
    
    $models = @(
        @{Name="llama3.2:3b"; Description="Llama 3.2 3B - Balanced performance"},
        @{Name="llama3.2:1b"; Description="Llama 3.2 1B - Lightweight option"}
    )
    
    $successCount = 0
    foreach ($model in $models) {
        Write-Host "📦 Downloading $($model.Description)..." -ForegroundColor Blue
        try {
            $process = Start-Process -FilePath "ollama" -ArgumentList "pull", $model.Name -Wait -PassThru -NoNewWindow
            if ($process.ExitCode -eq 0) {
                Write-Host "✅ $($model.Name) downloaded successfully" -ForegroundColor Green
                $successCount++
            }
            else {
                Write-Host "❌ Failed to download $($model.Name)" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "❌ Failed to download $($model.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    if ($successCount -gt 0) {
        Write-Host "✅ Successfully downloaded $successCount/$($models.Count) models" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "⚠️  No models were downloaded successfully" -ForegroundColor Yellow
        return $false
    }
}

function Setup-OllamaComplete {
    Write-Host "🤖 Complete Ollama setup..." -ForegroundColor Cyan
    
    # Check if admin required and restart if needed
    if (-not (Test-Administrator)) {
        Restart-AsAdmin
        return
    }
    
    # Install Ollama
    if (-not (Install-OllamaWindows)) {
        Write-Host "❌ Ollama installation failed" -ForegroundColor Red
        return $false
    }
    
    # Start service
    if (-not (Start-OllamaService)) {
        Write-Host "❌ Failed to start Ollama service" -ForegroundColor Red
        return $false
    }
    
    # Install models
    Install-RecommendedModels
    
    Write-Host "🎉 Ollama setup completed!" -ForegroundColor Green
    return $true
}

function Setup-EnvironmentEnhanced {
    Write-Host "🚀 Running enhanced complete setup..." -ForegroundColor Green
    
    # Check and install Ollama first
    try {
        ollama --version | Out-Null
        Write-Host "✅ Ollama already installed" -ForegroundColor Green
    }
    catch {
        Write-Host "🤖 Ollama not found, installing..." -ForegroundColor Yellow
        if (-not (Setup-OllamaComplete)) {
            Write-Host "⚠️  Continuing without Ollama..." -ForegroundColor Yellow
        }
    }
    
    # Run original setup
    Write-Host "🐍 Setting up Python environment..." -ForegroundColor Blue
    python setup.py
    
    # Ensure Ollama service is running
    Start-OllamaService | Out-Null
    
    Write-Host "🎉 Enhanced setup completed!" -ForegroundColor Green
}

function Create-EnhancedStartupScript {
    Write-Host "📜 Creating enhanced startup script..." -ForegroundColor Green
    
    $startupScript = @"
@echo off
echo Starting On-Device LLM Assistant...
cd /d "%~dp0"

REM Check if Ollama service is running
echo Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama service...
    start /B ollama serve
    echo Waiting for Ollama to start...
    timeout /t 10 /nobreak >nul
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the application
python launcher.py

pause
"@
    
    $startupScript | Out-File -FilePath "start_enhanced.bat" -Encoding ascii
    Write-Host "✅ Created start_enhanced.bat" -ForegroundColor Green
}

function List-Models {
    Write-Host "📋 Available Ollama models:" -ForegroundColor Cyan
    try {
        ollama list
    }
    catch {
        Write-Host "❌ Ollama not found or not running" -ForegroundColor Red
        Write-Host "Run: .\dev_enhanced.ps1 setup-ollama" -ForegroundColor Yellow
    }
}

function Pull-Models {
    Write-Host "📥 Pulling recommended models..." -ForegroundColor Green
    Start-OllamaService | Out-Null
    Install-RecommendedModels
}

function Serve-Models {
    Write-Host "🚀 Starting Ollama service..." -ForegroundColor Green
    Start-OllamaService
}

function Start-Application {
    Write-Host "🚀 Starting application..." -ForegroundColor Green
    
    # Ensure Ollama service is running
    Start-OllamaService | Out-Null
    
    # Start application
    & .\venv\Scripts\Activate.ps1
    python launcher.py
    deactivate
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

function Build-Project {
    Write-Host "🏗️ Building project..." -ForegroundColor Green
    
    if (Test-Path "frontend") {
        Set-Location frontend
        npm run build
        Set-Location ..
        Write-Host "✅ Frontend built successfully" -ForegroundColor Green
    }
}

function Show-Info {
    Write-Host "📊 Environment Information:" -ForegroundColor Cyan
    Write-Host "Python: $(python --version 2>&1)"
    Write-Host "Node: $(node --version 2>&1)"
    Write-Host "npm: $(npm --version 2>&1)"
    try {
        Write-Host "Ollama: $(ollama --version 2>&1)"
        
        # Check service status
        try {
            Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 | Out-Null
            Write-Host "Ollama Service: ✅ Running" -ForegroundColor Green
        }
        catch {
            Write-Host "Ollama Service: ❌ Not running" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "Ollama: ❌ Not installed" -ForegroundColor Red
    }
}

# Command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "setup" { Setup-EnvironmentEnhanced }
    "setup-ollama" { Setup-OllamaComplete }
    "install" { Install-Dependencies }
    "start" { Start-Application }
    "build" { Build-Project }
    "models-list" { List-Models }
    "models-pull" { Pull-Models }
    "models-serve" { Serve-Models }
    "info" { Show-Info }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
