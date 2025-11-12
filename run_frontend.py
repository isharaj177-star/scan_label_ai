"""
Run only the frontend server.
Press Ctrl+C to stop.
"""

import subprocess
import sys
import os
import signal


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nStopping frontend server...")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "=" * 60)
    print("  ScanLabel AI - Frontend Server")
    print("=" * 60)
    print("  Port: 8080")
    print("  URL: http://localhost:8080")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")
    
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    os.chdir(frontend_dir)
    
    try:
        subprocess.run(
            [sys.executable, "-m", "http.server", "8080"],
            check=True
        )
    except KeyboardInterrupt:
        signal_handler(None, None)

