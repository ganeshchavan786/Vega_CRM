"""
VEGA CRM - Windows Production Server
Simple one-click server for Windows 10/11
"""

import os
import sys
import webbrowser
import time
from threading import Timer

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def open_browser():
    """Open browser after server starts"""
    time.sleep(2)
    webbrowser.open('http://localhost:8000')

def main():
    print("=" * 50)
    print("       VEGA CRM - Production Server")
    print("=" * 50)
    print()
    print("Starting server...")
    print("Access URL: http://localhost:8000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    print()
    
    # Open browser in background
    Timer(2, open_browser).start()
    
    # Import and run uvicorn
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
