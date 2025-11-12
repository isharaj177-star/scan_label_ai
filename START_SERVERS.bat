@echo off
echo Starting ScanLabel AI Servers...
echo.

echo Starting Backend API on port 8000...
start "Backend API - CHECK THIS WINDOW FOR LOGS" cmd /k "cd /d %~dp0 && echo ======================================== && echo BACKEND STARTING - WATCH FOR LOGS && echo ======================================== && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server on port 8080...
start "Frontend Server" cmd /k "cd /d %~dp0\frontend && python -m http.server 8080"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Servers Started!
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:8080
echo API Docs: http://localhost:8000/docs
echo.
echo Opening frontend in browser...
start http://localhost:8080

echo.
echo Press any key to exit (servers will keep running)...
pause >nul

