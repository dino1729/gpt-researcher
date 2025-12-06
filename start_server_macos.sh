#!/bin/bash
# Startup script for GPT Researcher on macOS
# This sets the required library paths for PDF generation

# Set library paths for WeasyPrint (PDF generation)
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:${DYLD_LIBRARY_PATH}"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig"

echo "Starting GPT Researcher server with PDF generation support..."
echo "Library paths configured for Apple Silicon"
echo ""

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
