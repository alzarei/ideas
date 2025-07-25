@echo off
echo Starting On-Device LLM Assistant...
cd /d "%~dp0"

REM Check if Ollama service is running
echo Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the application
python launcher.py

pause
