#!/bin/bash
# Quick start script for GPT Researcher on Raspberry Pi with Docker :-)

echo "🐋🍓 GPT Researcher - Docker Setup for Raspberry Pi"
echo "===================================================="
echo ""

# Check if running on Linux
if [[ "$(uname)" != "Linux" ]]; then
    echo "⚠️  This script is designed for Raspberry Pi / Linux"
    echo "   For other systems, use: docker-compose up -d"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo ""
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo ""
    echo "✅ Docker installed! Please log out and back in, then run this script again."
    exit 0
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null && ! docker-compose --version &> /dev/null; then
    echo "❌ Docker Compose is not available!"
    echo "   Installing Docker Compose plugin..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo ""
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo "✅ .env file created"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
        echo "   nano .env"
        echo ""
        read -p "Press Enter after you've added your API keys, or Ctrl+C to exit..."
    else
        echo "Please create a .env file with your API keys:"
        echo "   OPENAI_API_KEY=your_key_here"
        echo "   TAVILY_API_KEY=your_key_here"
        exit 1
    fi
fi

# Detect Raspberry Pi model and suggest settings
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    PI_MODEL=$(grep "Model" /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)
    echo "🍓 Detected: $PI_MODEL"
    echo ""
    
    # Check memory
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_MEM" -lt 4 ]; then
        echo "⚠️  Warning: Low memory detected (${TOTAL_MEM}GB)"
        echo "   Consider:"
        echo "   - Increasing swap space"
        echo "   - Using lighter models"
        echo "   - Reducing MAX_ITERATIONS in .env"
        echo ""
    fi
fi

# Ask about local LLM
echo "Do you want to run with local LLM (Ollama) for privacy and cost savings?"
echo "This requires additional 2-4GB RAM and will download model files."
read -p "Enable Ollama? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    COMPOSE_PROFILE="--profile local-llm"
    echo "✅ Will start with Ollama support"
    echo ""
    echo "After startup, pull a model with:"
    echo "   docker exec -it ollama-pi ollama pull llama3.2:1b"
else
    COMPOSE_PROFILE=""
    echo "✅ Will use API-based LLM (OpenAI/Anthropic)"
fi

echo ""
echo "🏗️  Building Docker image (this may take 10-20 minutes on first run)..."
echo ""

# Build the image
docker compose -f docker-compose.raspberry-pi.yml build

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Build failed! Check the error messages above."
    exit 1
fi

echo ""
echo "✅ Build complete!"
echo ""
echo "🚀 Starting GPT Researcher..."
echo ""

# Start the containers
docker compose -f docker-compose.raspberry-pi.yml $COMPOSE_PROFILE up -d

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to start containers! Check the error messages above."
    exit 1
fi

echo ""
echo "✅ GPT Researcher is starting up!"
echo ""

# Wait for health check
echo "⏳ Waiting for services to be ready..."
sleep 5

# Show status
docker compose -f docker-compose.raspberry-pi.yml ps

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📍 Access GPT Researcher at:"
echo "   - Local: http://localhost:8000"
echo "   - Network: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "📊 Useful commands:"
echo "   - View logs:    docker compose -f docker-compose.raspberry-pi.yml logs -f"
echo "   - Stop:         docker compose -f docker-compose.raspberry-pi.yml down"
echo "   - Restart:      docker compose -f docker-compose.raspberry-pi.yml restart"
echo "   - Stats:        docker stats gpt-researcher-pi"
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🤖 Don't forget to pull an Ollama model:"
    echo "   docker exec -it ollama-pi ollama pull llama3.2:1b"
    echo ""
fi

echo "📚 Full documentation: DOCKER_RASPBERRY_PI.md"
echo ""

