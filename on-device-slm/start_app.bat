@echo off
echo ========================================
echo    On-Device LLM Assistant
echo ========================================
echo.
echo Starting your AI assistant...
echo This will open:
echo - Frontend (Chat Interface): http://localhost:3000
echo - Backend (API Server):     http://localhost:8000
echo.
echo Please wait 10-15 seconds for services to start...
echo.

REM Start backend in background
echo [1/2] Starting backend server...
cd /d "%~dp0"
start /B py launcher.py

REM Start frontend
echo [2/2] Starting frontend server...
cd frontend
start /B cmd /k "npm start"

echo.
echo ✅ Both services are starting!
echo.
echo 🌐 Frontend (Chat): http://localhost:3000
echo ⚙️  Backend (API):   http://localhost:8000
echo.
echo 💡 The chat interface will open in your browser shortly.
echo 💡 Close this window to stop all services.
echo.
echo Press any key to stop all services...
pause >nul

REM Kill processes when done
echo.
echo Stopping services...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
echo Services stopped. You can now close this window.
pause
