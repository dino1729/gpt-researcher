#!/bin/bash
# Setup script for GPT Researcher on Raspberry Pi :-)
# This installs all system dependencies needed for PDF generation

echo "🍓 GPT Researcher - Raspberry Pi Setup Script"
echo "=============================================="
echo ""

# Check if running on Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "⚠️  This script is designed for Raspberry Pi / Linux systems"
    echo "   For macOS, use: brew install cairo pango gdk-pixbuf libffi gobject-introspection"
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install WeasyPrint system dependencies
echo "📚 Installing WeasyPrint dependencies for PDF generation..."
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

echo ""
echo "✅ System dependencies installed!"
echo ""

# Check if virtual environment exists
if [ -d ".venv311" ] || [ -d "venv" ]; then
    echo "📦 Installing/updating Python packages..."
    
    # Activate virtual environment
    if [ -d ".venv311" ]; then
        source .venv311/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Install/upgrade Python packages
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Python packages installed!"
else
    echo "⚠️  No virtual environment found (.venv311 or venv)"
    echo "   Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "📦 Installing Python packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Virtual environment created and packages installed!"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the server, run:"
echo "   ./start_server.sh"
echo ""
echo "Or manually:"
echo "   source venv/bin/activate  # or .venv311/bin/activate"
echo "   python -m uvicorn backend.server.server:app --host=0.0.0.0 --port=8000"
echo ""

