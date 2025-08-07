# Enhanced On-Device LLM Assistant - PowerShell Development Script
# Usage: .\dev_enhanced.ps1 [command] [-Force]
# Author: Auto-generated with timeout-based Ollama installation

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [switch]$Force,
    [switch]$SkipOllama,
    [switch]$Quick
)

function Test-Command($cmd) {
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Restart-AsAdmin {
    if (-not (Test-Administrator)) {
        Write-Host "Administrator privileges required for Ollama installation..." -ForegroundColor Yellow
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
    Write-Host "  setup-ollama   - Install Ollama with timeout protection"
    Write-Host "  install        - Install dependencies only"
    Write-Host ""
    Write-Host "Run Commands:" -ForegroundColor Yellow
    Write-Host "  start          - Start the full application"
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
    Write-Host "  info           - Show environment information"
    Write-Host ""
    Write-Host "Flags:" -ForegroundColor Green
    Write-Host "  -Force         - Force reinstallation"
    Write-Host "  -SkipOllama    - Skip Ollama installation"
    Write-Host "  -Quick         - Quick setup without frontend build"
    Write-Host ""
    Write-Host "Usage: .\dev_enhanced.ps1 <command> [-Force] [-SkipOllama] [-Quick]" -ForegroundColor Green
}

function Install-OllamaWindows {
    Write-Host "Installing Ollama with timeout protection..." -ForegroundColor Blue
    
    # Check if already installed
    try {
        $version = ollama --version 2>$null
        if ($version -and -not $Force) {
            Write-Host "Ollama already installed: $version" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Not installed, continue
    }
    
    $downloadUrl = "https://ollama.ai/download/OllamaSetup.exe"
    $tempDir = Join-Path $env:TEMP "OllamaInstall"
    $installerPath = Join-Path $tempDir "OllamaSetup.exe"
    
    try {
        # Create temp directory
        if (-not (Test-Path $tempDir)) {
            New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
        }
        
        # Download installer
        Write-Host "Downloading Ollama installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        
        # Install with timeout using jobs
        Write-Host "Installing Ollama (with 3-minute timeout)..." -ForegroundColor Yellow
        $job = Start-Job -ScriptBlock {
            param($installerPath)
            $process = Start-Process -FilePath $installerPath -ArgumentList "/S", "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART" -Wait -PassThru
            return $process.ExitCode
        } -ArgumentList $installerPath
        
        # Wait for job with timeout
        if (Wait-Job -Job $job -Timeout 180) {
            $exitCode = Receive-Job -Job $job
            Remove-Job -Job $job
            
            if ($exitCode -eq 0) {
                Write-Host "Ollama installed successfully!" -ForegroundColor Green
                
                # Add to PATH if needed
                $ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama"
                if ((Test-Path $ollamaPath) -and ($env:PATH -notlike "*$ollamaPath*")) {
                    $env:PATH += ";$ollamaPath"
                }
                
                # Refresh environment variables
                $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
                
                return $true
            }
            else {
                Write-Host "Installation failed with exit code: $exitCode" -ForegroundColor Red
                return $false
            }
        }
        else {
            # Timeout occurred
            Write-Host "Installation timed out after 3 minutes, killing installer..." -ForegroundColor Yellow
            Remove-Job -Job $job -Force
            taskkill /f /im OllamaSetup.exe 2>&1 | Out-Null
            
            # Check if Ollama was actually installed despite timeout
            Start-Sleep -Seconds 5
            try {
                $version = ollama --version 2>$null
                if ($version) {
                    Write-Host "Ollama appears to have installed successfully despite timeout" -ForegroundColor Green
                    return $true
                }
            }
            catch {}
            
            Write-Host "Installation failed (timeout)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Installation failed: $($_.Exception.Message)" -ForegroundColor Red
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
    Write-Host "Starting Ollama service..." -ForegroundColor Green
    
    # Check if already running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "Ollama service is already running" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Not running, start it
    }
    
    try {
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        # Verify service started
        $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "Ollama service started successfully" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "Ollama service may not be responding yet" -ForegroundColor Yellow
        return $false
    }
}

function Setup-Environment {
    Write-Host "Enhanced Development Environment Setup" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan

    # 1. Check and setup Python
    Write-Host "Checking Python..." -ForegroundColor Blue
    $pythonExe = $null
    $pythonFound = $false

    foreach ($cmd in @('python', 'python3', 'py')) {
        if (Test-Command $cmd) {
            try {
                $ver = & $cmd --version 2>&1
                if ($ver -match 'Python' -and $ver -notmatch 'Microsoft Store') {
                    $pythonExe = (Get-Command $cmd).Source
                    $pythonFound = $true
                    Write-Host "$cmd found: $ver" -ForegroundColor Green
                    break
                }
            } catch {}
        }
    }

    if (-not $pythonFound) {
        Write-Host "Python not found. Installing..." -ForegroundColor Yellow
        winget install --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
        
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
        
        foreach ($cmd in @('python', 'python3', 'py')) {
            if (Test-Command $cmd) {
                $pythonExe = (Get-Command $cmd).Source
                $pythonFound = $true
                Write-Host "Python installed successfully" -ForegroundColor Green
                break
            }
        }
    }

    # 2. Check Node.js
    Write-Host "Checking Node.js..." -ForegroundColor Blue
    if (-not (Test-Command node)) {
        Write-Host "Node.js not found. Installing..." -ForegroundColor Yellow
        winget install --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
        
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
        
        if (Test-Command node) {
            Write-Host "Node.js installed successfully" -ForegroundColor Green
        }
    } else {
        Write-Host "Node.js found: $(node --version)" -ForegroundColor Green
    }

    # 3. Handle Ollama installation
    if (-not $SkipOllama) {
        Write-Host "Checking Ollama..." -ForegroundColor Blue
        if (-not (Test-Command ollama)) {
            $ollamaInstalled = Install-OllamaWindows
            if (-not $ollamaInstalled) {
                Write-Host "Warning: Ollama installation failed, but continuing..." -ForegroundColor Yellow
            }
        } else {
            Write-Host "Ollama found: $(ollama --version)" -ForegroundColor Green
        }
    } else {
        Write-Host "Skipping Ollama installation" -ForegroundColor Yellow
    }

    # 4. Run Python setup
    Write-Host "Setting up Python environment..." -ForegroundColor Blue
    if (Test-Path "setup.py") {
        & $pythonExe setup.py
    } else {
        Write-Host "setup.py not found, installing requirements directly..." -ForegroundColor Yellow
        if (Test-Path "requirements.txt") {
            & $pythonExe -m pip install -r requirements.txt
        }
    }

    # 5. Setup frontend
    Write-Host "Setting up frontend..." -ForegroundColor Blue
    if (Test-Path "frontend") {
        Set-Location frontend
        if (Test-Command npm) {
            npm install
            if (-not $Quick) {
                Write-Host "Building frontend..." -ForegroundColor Yellow
                npm run build
            }
        }
        Set-Location ..
    }

    Write-Host "Setup completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To start the application:" -ForegroundColor Cyan
    Write-Host "  Backend: py launcher.py" -ForegroundColor White
    Write-Host "  Frontend: cd frontend && npm start" -ForegroundColor White

    if (-not $SkipOllama -and (Test-Command ollama)) {
        Write-Host "  Ollama: ollama serve" -ForegroundColor White
    }
}

function Start-Application {
    Write-Host "Starting full application..." -ForegroundColor Green
    
    # Ensure Ollama service is running
    if (Test-Command ollama) {
        Start-OllamaService | Out-Null
    }
    
    # Start backend
    Write-Host "Starting backend..." -ForegroundColor Blue
    Start-Process -FilePath "py" -ArgumentList "launcher.py" -WindowStyle Normal
    
    # Start frontend
    if (Test-Path "frontend") {
        Write-Host "Starting frontend..." -ForegroundColor Blue
        Set-Location frontend
        Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Normal
        Set-Location ..
    }
}

function Show-Info {
    Write-Host "Environment Information:" -ForegroundColor Cyan
    
    if (Test-Command python) {
        Write-Host "Python: $(python --version 2>&1)" -ForegroundColor Green
    } else {
        Write-Host "Python: Not installed" -ForegroundColor Red
    }
    
    if (Test-Command node) {
        Write-Host "Node.js: $(node --version 2>&1)" -ForegroundColor Green
    } else {
        Write-Host "Node.js: Not installed" -ForegroundColor Red
    }
    
    if (Test-Command npm) {
        Write-Host "npm: $(npm --version 2>&1)" -ForegroundColor Green
    } else {
        Write-Host "npm: Not installed" -ForegroundColor Red
    }
    
    if (Test-Command ollama) {
        Write-Host "Ollama: $(ollama --version 2>&1)" -ForegroundColor Green
        
        # Check service status
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 3 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "Ollama Service: Running" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "Ollama Service: Not running" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Ollama: Not installed" -ForegroundColor Red
    }
}

# Command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "setup" { Setup-Environment }
    "setup-ollama" { Install-OllamaWindows }
    "start" { Start-Application }
    "start-backend" { 
        if (Test-Command ollama) { Start-OllamaService | Out-Null }
        & py launcher.py
    }
    "start-frontend" { 
        if (Test-Path "frontend") {
            Set-Location frontend
            npm start
            Set-Location ..
        }
    }
    "models-list" { 
        if (Test-Command ollama) { ollama list } 
        else { Write-Host "Ollama not installed" -ForegroundColor Red }
    }
    "models-serve" { Start-OllamaService }
    "build" { 
        if (Test-Path "frontend") {
            Set-Location frontend
            npm run build
            Set-Location ..
        }
    }
    "info" { Show-Info }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
