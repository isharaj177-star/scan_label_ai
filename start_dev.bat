@echo off
cls
echo ========================================
echo   ScanLabel AI - Starting Servers
echo ========================================
echo.

REM Kill all Python processes and clear ports
echo [1/3] Stopping old servers...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 1 /nobreak >nul

REM Kill processes on port 8001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8001...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 1 /nobreak >nul
    taskkill /F /T /PID %%a >nul 2>&1
)

REM Kill processes on port 8080
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8080...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 1 /nobreak >nul
    taskkill /F /T /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

REM Wait a bit more for Windows to release ports
echo Waiting for ports to be released...
timeout /t 5 /nobreak >nul
echo Ports cleared!

echo [2/3] Starting Backend API (port 8001)...
start "BACKEND - Watch Logs Here" cmd /k "title BACKEND API - Port 8001 && cd /d %~dp0 && echo ======================================== && echo   BACKEND API SERVER && echo   Port: 8001 && echo   Logs appear below && echo ======================================== && echo. && python -m uvicorn main:app --host 0.0.0.0 --port 8001"

timeout /t 3 /nobreak >nul

echo [3/3] Starting Frontend Server (port 8080)...
start "FRONTEND - Port 8080" cmd /k "title FRONTEND SERVER - Port 8080 && cd /d %~dp0\frontend && echo ======================================== && echo   FRONTEND SERVER && echo   Port: 8080 && echo ======================================== && echo. && python -m http.server 8080"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Servers Started Successfully!
echo ========================================
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:8080
echo   API Docs: http://localhost:8001/docs
echo ========================================
echo.
echo Opening frontend in browser...
timeout /t 1 /nobreak >nul
start http://localhost:8080
echo.
echo Press any key to close this window (servers keep running)...
pause >nul

