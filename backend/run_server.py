#!/usr/bin/env python3
"""
GPT-Researcher Backend Server Startup Script

Run this to start the research API server.
"""

import uvicorn
import os
import sys
import platform

# Set library path for WeasyPrint on macOS :-)
if platform.system() == "Darwin":  # macOS
    machine = platform.machine()
    if machine == "arm64":
        # Apple Silicon
        lib_path = "/opt/homebrew/lib"
    else:
        # Intel Mac
        lib_path = "/usr/local/lib"
    
    current_dyld_path = os.environ.get("DYLD_LIBRARY_PATH", "")
    if lib_path not in current_dyld_path:
        os.environ["DYLD_LIBRARY_PATH"] = f"{lib_path}:{current_dyld_path}"
        print(f"📚 Set DYLD_LIBRARY_PATH for PDF generation support")

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start the server
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )



