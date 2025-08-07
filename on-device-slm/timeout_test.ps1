# Test Script for Timeout-Based Ollama Installation
# This script tests our timeout functionality specifically

param(
    [switch]$TestTimeout
)

function Test-Command($cmd) {
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

function Install-OllamaWithTimeout {
    Write-Host "Testing Ollama installation with 3-minute timeout..." -ForegroundColor Green
    
    # Check if already installed
    try {
        $version = ollama --version 2>$null
        if ($version) {
            Write-Host "Ollama already installed: $version" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Not installed, continue
    }
    
    $downloadUrl = "https://ollama.ai/download/OllamaSetup.exe"
    $tempDir = Join-Path $env:TEMP "OllamaTest"
    $installerPath = Join-Path $tempDir "OllamaSetup.exe"
    
    try {
        # Create temp directory
        if (-not (Test-Path $tempDir)) {
            New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
        }
        
        # Download installer
        Write-Host "Downloading Ollama installer..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Host "Starting timeout-protected installation (3 minutes max)..." -ForegroundColor Blue
        
        # Install with timeout using jobs
        $job = Start-Job -ScriptBlock {
            param($installerPath)
            $process = Start-Process -FilePath $installerPath -ArgumentList "/S", "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART" -Wait -PassThru
            return $process.ExitCode
        } -ArgumentList $installerPath
        
        # Wait for job with timeout (3 minutes)
        if (Wait-Job -Job $job -Timeout 180) {
            $exitCode = Receive-Job -Job $job
            Remove-Job -Job $job
            
            if ($exitCode -eq 0) {
                Write-Host "SUCCESS: Ollama installed!" -ForegroundColor Green
                return $true
            }
            else {
                Write-Host "FAILED: Installation failed with exit code: $exitCode" -ForegroundColor Red
                return $false
            }
        }
        else {
            # Timeout occurred
            Write-Host "TIMEOUT: Installation timed out, cleaning up..." -ForegroundColor Yellow
            Remove-Job -Job $job -Force
            taskkill /f /im OllamaSetup.exe 2>&1 | Out-Null
            
            # Check if it installed anyway
            Start-Sleep -Seconds 5
            try {
                $version = ollama --version 2>$null
                if ($version) {
                    Write-Host "SUCCESS: Ollama installed despite timeout!" -ForegroundColor Green
                    return $true
                }
            }
            catch {}
            
            Write-Host "FAILED: Timeout and no installation detected" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        # Cleanup
        if (Test-Path $tempDir) {
            Remove-Item $tempDir -Recurse -Force
        }
    }
}

# Main execution
Write-Host "=== Timeout Installation Test ===" -ForegroundColor Cyan

if ($TestTimeout) {
    $result = Install-OllamaWithTimeout
    
    if ($result) {
        Write-Host "=== TEST PASSED: Timeout system works! ===" -ForegroundColor Green
    } else {
        Write-Host "=== TEST FAILED: Issues with timeout system ===" -ForegroundColor Red
    }
} else {
    Write-Host "This script tests the timeout-based Ollama installation." -ForegroundColor Yellow
    Write-Host "Run with -TestTimeout to actually test the installation." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Example: .\timeout_test.ps1 -TestTimeout" -ForegroundColor Green
}
