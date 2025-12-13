#!/bin/bash
# Start script for GPT Researcher (Standalone)

# Set library path for WeasyPrint (PDF generation) on macOS
if [[ "$(uname)" == "Darwin" ]]; then
    if [[ $(uname -m) == "arm64" ]]; then
        export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
    else
        export DYLD_LIBRARY_PATH="/usr/local/lib:$DYLD_LIBRARY_PATH"
    fi
fi

# Create logs directory
mkdir -p logs

# Activate virtual environment if present
if [ -d ".venv311" ]; then
    source .venv311/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🚀 Starting GPT Researcher..."
# Start uvicorn in the background and save PID
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > logs/uvicorn.log 2>&1 &
PID=$!
echo $PID > logs/uvicorn.pid

echo "✅ Server started with PID $PID"
echo "📄 Logs: logs/uvicorn.log"
echo "🌐 URL: http://localhost:8000"
