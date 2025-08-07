# Universal One-Click Setup Script for On-Device LLM Assistant
# This script installs Python, Node.js, and Ollama if missing, then runs the full setup.

function Test-Command($cmd) {
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

Write-Host "Starting One-Click Setup for On-Device LLM Assistant..." -ForegroundColor Green

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
    Write-Host "Python not found. Installing via winget..." -ForegroundColor Yellow
    $wingetResult = winget install --id Python.Python.3 --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($wingetResult -match 'No package found matching input criteria' -or $wingetResult -match 'failed' -or $wingetResult -match 'error') {
        Write-Host "winget failed to install Python. Downloading from python.org..." -ForegroundColor Yellow
        $pythonInstaller = "$env:TEMP\\python-installer.exe"
        $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
        Write-Host "Running Python installer silently..." -ForegroundColor Yellow
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait
    }
    # Search common install locations
    $possibleDirs = @()
    $pf = $env:ProgramFiles
    $pf86 = ${env:ProgramFiles(x86)}
    $possibleDirs += "$env:LOCALAPPDATA\Programs\Python"
    if (Test-Path $pf) { $possibleDirs += Get-ChildItem -Path $pf -Directory -Filter Python* -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName } }
    if ($pf86 -and (Test-Path $pf86)) { $possibleDirs += Get-ChildItem -Path $pf86 -Directory -Filter Python* -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName } }
    foreach ($dir in $possibleDirs) {
        $found = Get-ChildItem -Path $dir -Recurse -Filter python.exe -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $pythonExe = $found.FullName
            $pythonFound = $true
            Write-Host "Python installed at $pythonExe" -ForegroundColor Green
            $env:PATH += ";$($pythonExe | Split-Path)"
            break
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
if (-not (Test-Command ollama)) {
    Write-Host "Ollama not found. Installing via winget..." -ForegroundColor Yellow
    $wingetResult = winget install --id Ollama.Ollama -e --silent --accept-package-agreements --accept-source-agreements --disable-interactivity --force 2>&1
    
    # Check if winget failed and fallback to direct download
    if ($wingetResult -match 'failed' -or $wingetResult -match 'error' -or -not (Test-Command ollama)) {
        Write-Host "Winget failed, downloading Ollama directly..." -ForegroundColor Yellow
        
        # Download and install silently
        $tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
        $installerPath = Join-Path $tempDir "OllamaSetup.exe"
        
        try {
            Invoke-WebRequest -Uri "https://ollama.ai/download/OllamaSetup.exe" -OutFile $installerPath
            Start-Process -FilePath $installerPath -ArgumentList "/S", "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART" -Wait -WindowStyle Hidden
            
            # Add to PATH for current session
            $ollamaPath = "${env:ProgramFiles}\Ollama"
            if ($env:PATH -notlike "*$ollamaPath*") {
                $env:PATH += ";$ollamaPath"
            }
            
            Write-Host "Ollama installation completed" -ForegroundColor Green
        }
        catch {
            Write-Host "Warning: Ollama installation failed, continuing without it..." -ForegroundColor Yellow
        }
        finally {
            if (Test-Path $tempDir) {
                Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
    else {
        Write-Host "Ollama installation completed" -ForegroundColor Green
    }
}
else {
    Write-Host "Ollama found: $(ollama --version)" -ForegroundColor Green
}

# 4. Run enhanced setup (using the fixed script)
Write-Host "Running enhanced setup..." -ForegroundColor Cyan

if ($pythonExe) {
    & $pythonExe --version
    # Use PowerShell to run dev_enhanced_fixed.ps1 setup
    powershell -ExecutionPolicy Bypass -File "dev_enhanced_fixed.ps1" setup
} else {
    Write-Host "Python executable not found for setup. Please check your installation." -ForegroundColor Red
    exit 1
}

Write-Host "All done! The app should be running or ready to start." -ForegroundColor Green
Write-Host "If the browser did not open, visit: http://localhost:8000" -ForegroundColor Cyan
