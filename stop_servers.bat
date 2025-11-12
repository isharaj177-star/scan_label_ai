@echo off
cls
echo ========================================
echo   ScanLabel AI - Stopping All Servers
echo ========================================
echo.

echo Stopping Backend (port 8001)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8001...
    taskkill /F /PID %%a >nul 2>&1
    taskkill /F /T /PID %%a >nul 2>&1
)

echo Stopping Frontend (port 8080)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo Killing process %%a on port 8080...
    taskkill /F /PID %%a >nul 2>&1
    taskkill /F /T /PID %%a >nul 2>&1
)

echo Stopping all Python processes...
taskkill /F /IM python.exe /T >nul 2>&1

timeout /t 2 /nobreak >nul
echo.
echo All servers stopped!
echo.
pause

