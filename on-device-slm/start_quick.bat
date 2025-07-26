@echo off
echo Starting On-Device LLM Assistant (Quick Mode)...
cd /d "%~dp0"

echo Note: No AI models installed yet.
echo You can download models from the web interface once the app starts.

call venv\Scripts\activate.bat
python launcher.py
pause
