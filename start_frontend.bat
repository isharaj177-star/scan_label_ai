@echo off
cls
echo ========================================
echo   ScanLabel AI - Frontend Server Only
echo ========================================
echo.

REM Kill any existing frontend on port 8080
echo Stopping old frontend server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8080...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 1 /nobreak >nul
    taskkill /F /T /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul
echo.

echo Starting Frontend Server...
echo   Port: 8080
echo   URL: http://localhost:8080
echo   Press Ctrl+C to stop
echo ========================================
echo.

cd /d %~dp0\frontend
python -m http.server 8080

pause

