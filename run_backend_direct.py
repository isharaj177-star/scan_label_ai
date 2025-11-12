"""
Run ONLY the backend server directly (no subprocess).
This ensures all logs appear immediately.
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
print("  Press Ctrl+C to stop")
print("=" * 60)
print()

# Run uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=True
    )

