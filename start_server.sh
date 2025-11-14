#!/bin/bash
# Startup script for GPT Researcher with PDF generation support :-)
# Works on macOS, Linux, and Raspberry Pi

echo "🚀 Starting GPT Researcher server..."

# Detect operating system
OS="$(uname)"

if [[ "$OS" == "Darwin" ]]; then
    # macOS - Set library path for WeasyPrint dependencies
    # This allows Python to find gobject, cairo, pango, etc.
    if [[ $(uname -m) == "arm64" ]]; then
        # Apple Silicon
        export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
        echo "📚 macOS (Apple Silicon) - Library path set for PDF generation"
    else
        # Intel Mac
        export DYLD_LIBRARY_PATH="/usr/local/lib:$DYLD_LIBRARY_PATH"
        echo "📚 macOS (Intel) - Library path set for PDF generation"
    fi
elif [[ "$OS" == "Linux" ]]; then
    # Linux (including Raspberry Pi)
    echo "🐧 Linux system detected"
    
    # Check if running on Raspberry Pi
    if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        echo "🍓 Raspberry Pi detected!"
    fi
    
    # On Linux, system libraries are usually in standard locations
    # No special LD_LIBRARY_PATH needed if installed via apt
    echo "📚 Using system libraries for PDF generation"
else
    echo "⚠️  Unknown operating system: $OS"
    echo "   Continuing anyway..."
fi

# Activate virtual environment if it exists
if [ -d ".venv311" ]; then
    source .venv311/bin/activate
    echo "✅ Virtual environment activated (.venv311)"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated (venv)"
else
    echo "⚠️  No virtual environment found"
    echo "   Continuing with system Python..."
fi

# Display Python version
PYTHON_VERSION=$(python --version 2>&1)
echo "🐍 Using: $PYTHON_VERSION"

# Start the server
echo ""
echo "Starting server on http://0.0.0.0:8000"
echo "Press CTRL+C to stop"
echo ""

python -m uvicorn backend.server.server:app --host=0.0.0.0 --port=8000 --reload

