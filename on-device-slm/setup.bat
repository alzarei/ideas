@echo off
echo ========================================
echo    On-Device LLM Assistant Setup
echo ========================================
echo.
echo This will automatically install and set up everything you need:
echo - Python (if missing)
echo - Node.js (if missing) 
echo - Ollama (if missing)
echo - All project dependencies
echo - Start the application
echo.
echo Please wait while we set everything up...
echo.
pause

powershell -ExecutionPolicy Bypass -File "one_click_setup_fixed.ps1"

echo.
echo ========================================
echo          Setup Complete!
echo ========================================
echo.
echo Your app is now running at:
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo For daily use, just double-click "start_both.bat"
echo.
pause
