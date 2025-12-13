#!/bin/bash
# Stop script for GPT Researcher

PID_FILE="logs/uvicorn.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "🛑 Stopping GPT Researcher (PID $PID)..."
        kill $PID
        
        # Wait for process to exit
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null; then
                break
            fi
            sleep 0.5
        done
        
        # Force kill if still running
        if ps -p $PID > /dev/null; then
            echo "⚠️  Force killing process..."
            kill -9 $PID
        fi
        
        rm "$PID_FILE"
        echo "✅ Server stopped."
    else
        echo "⚠️  Process $PID not found. Cleaning up PID file."
        rm "$PID_FILE"
    fi
else
    echo "ℹ️  No PID file found. Server might not be running."
fi

