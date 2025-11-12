@echo off
cls
echo ========================================
echo   ScanLabel AI - Backend Server Only
echo ========================================
echo.

REM Kill any existing backend on port 8001
echo Stopping old backend server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8001...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 1 /nobreak >nul
    taskkill /F /T /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul
echo.

echo Starting Backend API Server...
echo   Port: 8001
echo   API Docs: http://localhost:8001/docs
echo   Press Ctrl+C to stop
echo ========================================
echo.

cd /d %~dp0
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

pause

