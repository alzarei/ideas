@echo off
echo Starting On-Device LLM Assistant...
cd /d "%~dp0"

echo Checking for Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Ollama service...
    start /B ollama serve
    timeout /t 3 /nobreak >nul
)

call venv\Scripts\activate.bat
python launcher.py
pause
