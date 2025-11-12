"""
Run only the backend server DIRECTLY (no subprocess).
This ensures ALL logs appear immediately.
Press Ctrl+C to stop.
"""

import sys
import os

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("\n" + "=" * 60)
print("  ScanLabel AI - Backend Server")
print("=" * 60)
print("  Port: 8001")
print("  API Docs: http://localhost:8001/docs")
print("  ALL LOGS WILL APPEAR BELOW")
print("=" * 60)
print("\nPress Ctrl+C to stop\n")

# Run uvicorn directly - this ensures logs show up immediately
if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Force unbuffered output
    sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
    sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None
    
    print("=" * 60, flush=True)
    print("STARTING BACKEND SERVER", flush=True)
    print("=" * 60, flush=True)
    print("All logs will appear below:", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False,  # Disable reload to see errors clearly
        access_log=True  # Enable access logs
    )

