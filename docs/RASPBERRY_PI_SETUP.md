# GPT Researcher on Raspberry Pi 🍓 :-)

Complete guide for running GPT Researcher on Raspberry Pi (or any Debian/Ubuntu Linux system).

## System Requirements

- **Raspberry Pi 3 or newer** (Pi 4 or 5 recommended for better performance)
- **Raspberry Pi OS** (64-bit recommended) or Ubuntu
- **4GB+ RAM** (8GB recommended)
- **16GB+ SD card** (32GB+ recommended)
- **Internet connection**

## Quick Setup

### 1. Clone the Repository
```bash
cd ~
git clone https://github.com/assafelovic/gpt-researcher.git
cd gpt-researcher
```

### 2. Run Setup Script
```bash
chmod +x setup_raspberry_pi.sh
./setup_raspberry_pi.sh
```

This script will:
- ✅ Install all system dependencies for PDF generation
- ✅ Create/activate Python virtual environment
- ✅ Install all required Python packages

### 3. Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

Add your API keys:
```bash
OPENAI_API_KEY=your_openai_key_here
# Or other LLM provider keys
TAVILY_API_KEY=your_tavily_key_here  # Optional
```

### 4. Start the Server
```bash
./start_server.sh
```

The server will start on `http://0.0.0.0:8000`

Access from:
- **Same Pi**: http://localhost:8000
- **Other devices on network**: http://[raspberry-pi-ip]:8000

To find your Pi's IP address:
```bash
hostname -I
```

## Manual Installation (Alternative)

If you prefer manual setup:

### Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Python Packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Start Server
```bash
python -m uvicorn backend.server.server:app --host=0.0.0.0 --port=8000
```

## Performance Tips for Raspberry Pi

### 1. Use Local LLM (Optional)
For better performance and privacy, consider running a local LLM:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a lightweight model
ollama pull llama3.2:1b  # Small model for Pi 4/5
# or
ollama pull mistral:7b-instruct  # Larger, needs Pi 5 with 8GB RAM
```

Update `.env`:
```bash
LLM_PROVIDER=ollama
FAST_LLM_MODEL=llama3.2:1b
SMART_LLM_MODEL=llama3.2:1b
```

### 2. Optimize Memory Usage
```bash
# Increase swap if needed (for Pi with 4GB RAM)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 3. Use Lightweight Report Types
- Prefer `quick_report` over `detailed_report`
- Set smaller `max_iterations` in config

### 4. Enable Caching
Uncomment caching in `.env`:
```bash
ENABLE_CACHE=true
CACHE_TTL=3600
```

## Troubleshooting

### PDF Generation Issues

**Problem**: PDF generation fails
```bash
Error: cannot load library 'libgobject-2.0-0'
```

**Solution**:
```bash
# Install missing libraries
sudo apt-get install -y libgobject-2.0-0 libcairo2 libpango-1.0-0

# Verify installation
ldconfig -p | grep -E "(cairo|pango|gobject)"
```

### Memory Issues

**Problem**: Process killed or "Out of memory"

**Solution**:
```bash
# Check memory usage
free -h

# Increase swap (see Performance Tips above)
# Or use a lighter LLM model
```

### Slow Performance

**Problem**: Research takes a long time

**Solution**:
- Use `quick_report` instead of `detailed_report`
- Reduce `max_iterations` in config
- Use local LLM with smaller model
- Ensure you have good internet connection for API calls

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process (replace PID with actual number)
kill -9 PID

# Or use a different port
python -m uvicorn backend.server.server:app --host=0.0.0.0 --port=8001
```

## Running as a Service (Auto-start on Boot)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/gpt-researcher.service
```

Add:
```ini
[Unit]
Description=GPT Researcher Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/gpt-researcher
Environment="PATH=/home/pi/gpt-researcher/venv/bin"
ExecStart=/home/pi/gpt-researcher/venv/bin/python -m uvicorn backend.server.server:app --host=0.0.0.0 --port=8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gpt-researcher
sudo systemctl start gpt-researcher

# Check status
sudo systemctl status gpt-researcher

# View logs
sudo journalctl -u gpt-researcher -f
```

## Remote Access

### Using SSH Tunnel (Secure)
From your computer:
```bash
ssh -L 8000:localhost:8000 pi@raspberry-pi-ip
```

Then access: http://localhost:8000

### Using ngrok (Public URL)
```bash
# Install ngrok on Raspberry Pi
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update
sudo apt install ngrok

# Run ngrok
ngrok http 8000
```

## Hardware Recommendations

| Model | RAM | Performance | Recommendation |
|-------|-----|-------------|----------------|
| Pi 3B+ | 1GB | Slow | Not recommended |
| Pi 4 (4GB) | 4GB | Good | Minimum recommended |
| Pi 4 (8GB) | 8GB | Better | Good for production |
| Pi 5 (8GB) | 8GB | Best | Best for local LLM |

## Security Tips

1. **Change default password**: `passwd`
2. **Use SSH keys** instead of passwords
3. **Enable firewall**:
```bash
sudo apt-get install ufw
sudo ufw allow 22
sudo ufw allow 8000
sudo ufw enable
```
4. **Keep system updated**:
```bash
sudo apt-get update && sudo apt-get upgrade -y
```
5. **Don't expose to public internet** without proper security

## Support

For issues specific to Raspberry Pi:
1. Check logs: `tail -f logs/uvicorn.log`
2. Check system logs: `sudo journalctl -xe`
3. Monitor resources: `htop` or `top`
4. Check temperature: `vcgencmd measure_temp`

For general GPT Researcher issues:
- GitHub: https://github.com/assafelovic/gpt-researcher
- Discord: https://discord.gg/spBgZmm3Xe
- Docs: https://docs.gptr.dev/

---

Made with ❤️ for the Raspberry Pi community :-)

