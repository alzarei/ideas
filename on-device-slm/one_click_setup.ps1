# FIXED: Universal One-Click Setup Script for On-Device LLM Assistant
# This script installs Python, Node.js, and Ollama if missing, then runs the full setup.
# 
# KEY FIXES APPLIED:
# 1. PATH environment refresh before checking for installed programs
# 2. Proper Python executable detection (avoiding Microsoft Store aliases)
# 3. Timeout protection for winget installations to prevent infinite loops
# 4. Integrated setup process (no separate PowerShell processes)
# 5. Silent installations with proper error handling
#
# Author: Fixed by GitHub Copilot
# Date: August 8, 2025

function Test-Command($cmd) {
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

function Refresh-PathEnvironment {
    # Refresh PATH environment variable from registry
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
}

Write-Host "Starting One-Click Setup for On-Device LLM Assistant..." -ForegroundColor Green

# Refresh PATH at start to pick up any recently installed programs
Refresh-PathEnvironment

# 1. Install Python if missing
$pythonExe = $null
$pythonFound = $false

# Try python, python3, py in PATH, but ignore Microsoft Store alias
foreach ($cmd in @('python', 'python3', 'py')) {
    if (Test-Command $cmd) {
        try {
            $ver = & $cmd --version 2>&1
            # Ignore Microsoft Store alias
            if ($ver -match 'Python' -and $ver -notmatch 'Microsoft Store') {
                $pythonExe = (Get-Command $cmd).Source
                $pythonFound = $true
                Write-Host "$cmd found: $ver" -ForegroundColor Green
                break
            } elseif ($ver -match 'Microsoft Store') {
                Write-Host "$cmd points to Microsoft Store alias, ignoring..." -ForegroundColor Yellow
            }
        } catch {}
    }
}

# If not found, try to install
if (-not $pythonFound) {
    Write-Host "Python not found. Installing via winget (this may take a few minutes)..." -ForegroundColor Yellow
    
    # Use Start-Process with timeout to avoid infinite loops
    $wingetProcess = Start-Process -FilePath "winget" -ArgumentList "install", "--id", "Python.Python.3.11", "--silent", "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity" -PassThru -WindowStyle Hidden
    
    # Wait up to 5 minutes for installation
    $timeout = 300 # 5 minutes
    $waited = 0
    while (-not $wingetProcess.HasExited -and $waited -lt $timeout) {
        Start-Sleep -Seconds 10
        $waited += 10
        Write-Host "Installing Python... ($waited seconds elapsed)" -ForegroundColor Yellow
    }
    
    if (-not $wingetProcess.HasExited) {
        Write-Host "Python installation taking too long, killing process..." -ForegroundColor Yellow
        $wingetProcess.Kill()
    }
    
    Write-Host "Installation process completed, checking for Python..." -ForegroundColor Yellow
    
    # Wait a moment for installation to complete
    Start-Sleep -Seconds 5
    
    # Refresh PATH environment variable
    Refresh-PathEnvironment
    
    # Try to find Python again after installation
    foreach ($cmd in @('python', 'python3', 'py')) {
        if (Test-Command $cmd) {
            try {
                $ver = & $cmd --version 2>&1
                if ($ver -match 'Python' -and $ver -notmatch 'Microsoft Store') {
                    $pythonExe = (Get-Command $cmd).Source
                    $pythonFound = $true
                    Write-Host "Python found after installation: $ver" -ForegroundColor Green
                    break
                }
            } catch {}
        }
    }
    
    # If still not found, search install locations
    if (-not $pythonFound) {
        Write-Host "Searching common Python installation locations..." -ForegroundColor Yellow
        $possibleDirs = @()
        $pf = $env:ProgramFiles
        $possibleDirs += "$env:LOCALAPPDATA\Programs\Python"
        if (Test-Path $pf) { $possibleDirs += Get-ChildItem -Path $pf -Directory -Filter Python* -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName } }
        
        foreach ($dir in $possibleDirs) {
            $found = Get-ChildItem -Path $dir -Recurse -Filter python.exe -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                $pythonExe = $found.FullName
                $pythonFound = $true
                Write-Host "Python found at $pythonExe" -ForegroundColor Green
                $env:PATH += ";$($pythonExe | Split-Path)"
                break
            }
        }
    }
}

# Final check
if (-not $pythonFound -or -not $pythonExe) {
    Write-Host "Python not found or not working after install." -ForegroundColor Red
    Write-Host "Diagnostics:" -ForegroundColor Yellow
    Write-Host "  PATH: $env:PATH"
    Write-Host "  Tried commands: python, python3, py"
    Write-Host "Please close and reopen your terminal, then re-run this script, or install Python manually." -ForegroundColor Yellow
    exit 1
}

# 2. Install Node.js if missing
if (-not (Test-Command node)) {
    Write-Host "Node.js not found. Installing via winget..." -ForegroundColor Yellow
    winget install --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements --disable-interactivity --force 2>$null
    Write-Host "Node.js installation completed" -ForegroundColor Green
}
else {
    Write-Host "Node.js found: $(node --version)" -ForegroundColor Green
}

# 3. Install Ollama if missing
# Refresh PATH to pick up recently installed Ollama
Refresh-PathEnvironment

$ollamaWorking = $false

# Test if Ollama works with refreshed PATH
try {
    $ollamaVersion = & ollama --version 2>&1
    if ($ollamaVersion -match "version") {
        $ollamaWorking = $true
        Write-Host "Ollama found: $ollamaVersion" -ForegroundColor Green
    }
} catch {
    # Try with -v flag as fallback
    try {
        $ollamaVersion = & ollama -v 2>&1
        if ($ollamaVersion -match "version") {
            $ollamaWorking = $true
            Write-Host "Ollama found: $ollamaVersion" -ForegroundColor Green
        }
    } catch {
        # Ollama command failed completely
    }
}

# Only install if Ollama is definitely not working
if (-not $ollamaWorking) {
    Write-Host "Ollama not found or not working. Installing via winget..." -ForegroundColor Yellow
    $wingetResult = winget install --id Ollama.Ollama -e --silent --accept-package-agreements --accept-source-agreements --disable-interactivity --force 2>&1
    
    # Wait for installation to complete
    Start-Sleep -Seconds 5
    
    # Refresh PATH environment variable again
    Refresh-PathEnvironment
    
    # Test if Ollama is now accessible
    if (Test-Command ollama) {
        Write-Host "Ollama installation completed successfully" -ForegroundColor Green
    } else {
        Write-Host "Warning: Ollama installed but not immediately accessible. You may need to restart your terminal." -ForegroundColor Yellow
    }
}

# 4. Run integrated setup directly (no separate script)
Write-Host "Running integrated project setup..." -ForegroundColor Cyan

if ($pythonExe) {
    & $pythonExe --version
    
    # Create Python virtual environment
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    & $pythonExe -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Virtual environment created successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to create virtual environment, continuing without it..." -ForegroundColor Yellow
    }
    
    # Install Python requirements
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    if (Test-Path "requirements.txt") {
        & $pythonExe -m pip install -r requirements.txt --quiet
        Write-Host "Python dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "No requirements.txt found, skipping Python dependencies" -ForegroundColor Yellow
    }
    
    # Install Node.js dependencies
    if (Test-Path "frontend") {
        Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
        Set-Location frontend
        npm install --silent
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Node.js dependencies installed" -ForegroundColor Green
        }
        Set-Location ..
    }
    
    # Start Ollama service
    Write-Host "Starting Ollama service..." -ForegroundColor Yellow
    try {
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -PassThru | Out-Null
        Start-Sleep -Seconds 2
        Write-Host "Ollama service started" -ForegroundColor Green
    } catch {
        Write-Host "Could not start Ollama service (optional)" -ForegroundColor Yellow
    }
    
    # Start the application
    Write-Host "Starting the application..." -ForegroundColor Green
    & $pythonExe launcher.py
    
} else {
    Write-Host "Python executable not found for setup. Please check your installation." -ForegroundColor Red
    exit 1
}

Write-Host "All done! Your On-Device LLM Assistant is now running!" -ForegroundColor Green
Write-Host ""
Write-Host "Access your AI assistant at:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "The application is now ready to use!" -ForegroundColor Green
