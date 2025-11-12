#!/usr/bin/env python3
"""
Simple dev server startup script - runs both backend and frontend
Like 'npm run dev' but for Python
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Change to project root
project_root = Path(__file__).parent
os.chdir(project_root)

print("=" * 60)
print("🚀 Starting ScanLabel AI Development Servers")
print("=" * 60)
print()

# Kill any existing processes on ports 8000 and 8080
print("🔍 Checking for existing servers...")
try:
    import socket
    for port in [8000, 8080]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print(f"⚠️  Port {port} is in use - trying to free it...")
            # Try to kill process on this port (Windows)
            if sys.platform == 'win32':
                import subprocess
                try:
                    result = subprocess.run(
                        f'netstat -ano | findstr :{port}',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            parts = line.split()
                            if len(parts) > 0:
                                pid = parts[-1]
                                try:
                                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                                    print(f"   ✅ Killed process {pid} on port {port}")
                                except:
                                    pass
                except:
                    pass
        sock.close()
except:
    pass

time.sleep(1)

print()
print("📦 Starting Backend API (port 8000)...")
backend_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=project_root,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

time.sleep(3)

print("🌐 Starting Frontend Server (port 8080)...")
frontend_dir = project_root / "frontend"
frontend_process = subprocess.Popen(
    [sys.executable, "-m", "http.server", "8080"],
    cwd=frontend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

time.sleep(2)

print()
print("=" * 60)
print("✅ SERVERS STARTED!")
print("=" * 60)
print()
print("📍 Backend API:  http://localhost:8000")
print("📍 Frontend:     http://localhost:8080")
print("📍 API Docs:     http://localhost:8000/docs")
print()
print("📋 Backend logs will appear below:")
print("=" * 60)
print()

# Function to handle Ctrl+C
def signal_handler(sig, frame):
    print("\n\n🛑 Shutting down servers...")
    backend_process.terminate()
    frontend_process.terminate()
    backend_process.wait()
    frontend_process.wait()
    print("✅ Servers stopped")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Print backend output in real-time
try:
    for line in iter(backend_process.stdout.readline, ''):
        if line:
            print(line.rstrip())
except KeyboardInterrupt:
    signal_handler(None, None)








