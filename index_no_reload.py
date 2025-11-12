"""
Run both backend and frontend servers together in one terminal.
WITHOUT auto-reload (cleaner logs, but you need to restart manually).
Press Ctrl+C to stop both servers.
"""

import subprocess
import sys
import os
import signal
import time
from threading import Thread

# Store process references
backend_process = None
frontend_process = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nStopping servers...")
    if backend_process:
        backend_process.terminate()
    if frontend_process:
        frontend_process.terminate()
    
    # Wait a bit for graceful shutdown
    time.sleep(1)
    
    # Force kill if still running
    if backend_process and backend_process.poll() is None:
        backend_process.kill()
    if frontend_process and frontend_process.poll() is None:
        frontend_process.kill()
    
    print("Servers stopped!")
    sys.exit(0)


def run_backend():
    """Run backend server."""
    global backend_process
    print("[BACKEND] Starting on port 8001...", flush=True)
    print("[BACKEND] API Docs: http://localhost:8001/docs", flush=True)
    print("[BACKEND] Logs will appear below:", flush=True)
    print("[BACKEND] Note: Auto-reload is DISABLED (cleaner logs)", flush=True)
    print("=" * 60, flush=True)
    print()
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # NO --reload flag = no reload errors, but manual restart needed
    backend_process = subprocess.Popen(
        [sys.executable, "-u", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info"],
        stdout=sys.stdout,
        stderr=sys.stderr,
        bufsize=0,  # Unbuffered
        env={**os.environ, "PYTHONUNBUFFERED": "1"}  # Force unbuffered
    )
    backend_process.wait()


def run_frontend():
    """Run frontend server."""
    global frontend_process
    # Wait a bit for backend to start
    time.sleep(2)
    
    print("[FRONTEND] Starting on port 8080...", flush=True)
    print("[FRONTEND] URL: http://localhost:8080", flush=True)
    print("[FRONTEND] (Frontend logs are minimal)", flush=True)
    print("=" * 60, flush=True)
    print()
    
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    os.chdir(frontend_dir)
    # Frontend server is simple, redirect its output to reduce noise
    frontend_process = subprocess.Popen(
        [sys.executable, "-u", "-m", "http.server", "8080"],
        stdout=subprocess.PIPE,  # Don't show frontend logs (they're just HTTP requests)
        stderr=subprocess.PIPE,
        bufsize=0
    )
    frontend_process.wait()


if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "=" * 60)
    print("  ScanLabel AI - Starting Servers")
    print("=" * 60)
    print("  Press Ctrl+C to stop both servers")
    print("  Note: Auto-reload is DISABLED for cleaner logs")
    print("=" * 60)
    print()
    
    # Start backend in a thread
    backend_thread = Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in a thread
    frontend_thread = Thread(target=run_frontend, daemon=True)
    frontend_thread.start()
    
    # Keep main thread alive
    try:
        # Wait for either process to finish
        while True:
            if backend_process and backend_process.poll() is not None:
                print("\nBackend server stopped!")
                break
            if frontend_process and frontend_process.poll() is not None:
                print("\nFrontend server stopped!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

