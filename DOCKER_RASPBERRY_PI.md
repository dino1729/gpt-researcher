# GPT Researcher on Raspberry Pi with Docker 🐋🍓 :-)

Complete guide for running GPT Researcher in Docker on Raspberry Pi. All your fixes (chat feature, PDF generation) are included!

## Prerequisites

### 1. Hardware Requirements
- **Raspberry Pi 4 (4GB+)** or **Raspberry Pi 5** (8GB recommended)
- **32GB+ SD card** (class 10 or better)
- **Active cooling** (fan or heatsink) - Docker can be resource-intensive
- **Stable power supply** (official PSU recommended)

### 2. Software Requirements
- **Raspberry Pi OS 64-bit** (Bullseye or newer)
- **Docker** installed
- **Docker Compose** installed
- **Git** installed

## Quick Start (3 Steps!)

### Step 1: Install Docker
```bash
# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (no need for sudo)
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
docker-compose --version
```

### Step 2: Clone and Configure
```bash
# Clone the repository
git clone https://github.com/assafelovic/gpt-researcher.git
cd gpt-researcher

# Create environment file
cp .env.example .env
nano .env
```

Add your API keys:
```bash
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here  # Optional but recommended
```

### Step 3: Build and Run
```bash
# Build and start the container
docker-compose -f docker-compose.raspberry-pi.yml up -d

# Watch the logs
docker-compose -f docker-compose.raspberry-pi.yml logs -f
```

**That's it!** 🎉 Access at: `http://raspberry-pi-ip:8000`

## What's Included

### ✅ All Your Fixes
- **Chat Feature**: Fixed to pass report content properly
- **PDF Generation**: WeasyPrint dependencies included
- **ARM64 Support**: Optimized for Raspberry Pi architecture
- **Resource Management**: Memory and CPU limits configured

### ✅ System Dependencies
The Docker image includes:
- Python 3.11
- WeasyPrint libraries (cairo, pango, gdk-pixbuf, gobject)
- Chromium browser (ARM64 version)
- Firefox ESR
- All Python dependencies from requirements.txt

### ✅ Optimizations for Raspberry Pi
- Single worker process (lighter on RAM)
- Reduced iteration counts
- Proper resource limits
- Health checks
- Automatic restarts
- Log rotation

## Docker Commands

### Basic Operations
```bash
# Start services
docker-compose -f docker-compose.raspberry-pi.yml up -d

# Stop services
docker-compose -f docker-compose.raspberry-pi.yml down

# View logs
docker-compose -f docker-compose.raspberry-pi.yml logs -f

# Restart services
docker-compose -f docker-compose.raspberry-pi.yml restart

# Check status
docker-compose -f docker-compose.raspberry-pi.yml ps
```

### Maintenance
```bash
# Rebuild after code changes
docker-compose -f docker-compose.raspberry-pi.yml up -d --build

# View container stats (CPU, memory usage)
docker stats gpt-researcher-pi

# Access container shell
docker exec -it gpt-researcher-pi bash

# Clean up old images
docker system prune -a
```

### Logs and Debugging
```bash
# View last 100 lines
docker-compose -f docker-compose.raspberry-pi.yml logs --tail=100

# Follow logs in real-time
docker-compose -f docker-compose.raspberry-pi.yml logs -f gpt-researcher

# Check health status
docker inspect gpt-researcher-pi | grep -A 10 "Health"
```

## Configuration

### Resource Limits (Adjust in docker-compose.raspberry-pi.yml)

**For Raspberry Pi 4 (4GB)**:
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
```

**For Raspberry Pi 5 (8GB)**:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '3.0'
```

**For Raspberry Pi 3**:
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.5'
```

### Using Local LLM (Ollama)

For better performance and privacy, run Ollama locally:

```bash
# Start with Ollama included
docker-compose -f docker-compose.raspberry-pi.yml --profile local-llm up -d

# Pull a lightweight model (Pi 4/5)
docker exec -it ollama-pi ollama pull llama3.2:1b

# Or a larger model (Pi 5 with 8GB only)
docker exec -it ollama-pi ollama pull llama3.2:3b
```

Update `.env`:
```bash
LLM_PROVIDER=ollama
FAST_LLM_MODEL=llama3.2:1b
SMART_LLM_MODEL=llama3.2:1b
OLLAMA_BASE_URL=http://ollama:11434
```

### Performance Tuning

Edit `.env` for better Pi performance:

```bash
# Reduce iterations for faster research
MAX_ITERATIONS=2

# Reduce search results
MAX_SEARCH_RESULTS_PER_QUERY=3

# Use quick report type (set in UI or API)
REPORT_TYPE=quick_report

# Enable caching to reuse results
ENABLE_CACHE=true
CACHE_TTL=3600
```

## Troubleshooting

### Build Errors

**Problem**: Build fails or takes too long
```bash
# Increase build timeout
docker-compose -f docker-compose.raspberry-pi.yml build --no-cache

# If network issues occur
export DOCKER_BUILDKIT=0
docker-compose -f docker-compose.raspberry-pi.yml build
```

### Out of Memory

**Problem**: Container crashes or gets killed
```bash
# Check memory usage
docker stats gpt-researcher-pi

# Solution 1: Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Solution 2: Reduce memory limit in docker-compose.raspberry-pi.yml
```

### Slow Performance

**Problem**: Research takes very long

**Solutions**:
1. Use local LLM (Ollama) instead of API calls
2. Reduce `MAX_ITERATIONS` in `.env`
3. Use `quick_report` instead of `detailed_report`
4. Ensure Pi has good cooling (check: `vcgencmd measure_temp`)
5. Use ethernet instead of Wi-Fi

### PDF Generation Issues

**Problem**: PDFs fail to generate

**Check**:
```bash
# Verify WeasyPrint libraries are installed
docker exec -it gpt-researcher-pi dpkg -l | grep -E "cairo|pango|gobject"

# Test PDF generation
docker exec -it gpt-researcher-pi python -c "from weasyprint import HTML; print('✅ OK')"
```

### Container Won't Start

**Problem**: Container exits immediately

**Debug**:
```bash
# Check logs
docker-compose -f docker-compose.raspberry-pi.yml logs

# Run container interactively
docker run -it --rm gpt-researcher-pi bash

# Check environment variables
docker exec -it gpt-researcher-pi env | grep -E "OPENAI|TAVILY"
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
sudo lsof -i :8000

# Change port in docker-compose.raspberry-pi.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

## Accessing from Other Devices

### On Local Network
```bash
# Find Pi's IP address
hostname -I

# Access from any device
http://192.168.1.XXX:8000
```

### Remote Access (Secure)

**Option 1: SSH Tunnel** (recommended)
```bash
# From your computer
ssh -L 8000:localhost:8000 pi@raspberry-pi-ip

# Then access: http://localhost:8000
```

**Option 2: Tailscale** (easy VPN)
```bash
# Install on Raspberry Pi
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Install on your device, then access via Tailscale IP
```

**Option 3: ngrok** (public URL)
```bash
# Run ngrok
docker run -d --name ngrok \
  --link gpt-researcher-pi:gpt-researcher \
  -p 4040:4040 \
  ngrok/ngrok:latest http gpt-researcher:8000
```

## Auto-Start on Boot

Docker Compose with `restart: unless-stopped` already handles this!

To enable Docker on boot:
```bash
sudo systemctl enable docker
```

## Updating

When you make code changes or pull updates:

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.raspberry-pi.yml up -d --build

# Or if you want fresh build
docker-compose -f docker-compose.raspberry-pi.yml down
docker-compose -f docker-compose.raspberry-pi.yml build --no-cache
docker-compose -f docker-compose.raspberry-pi.yml up -d
```

## Backup and Restore

### Backup Research Data
```bash
# Backup outputs and logs
tar -czf gpt-researcher-backup-$(date +%Y%m%d).tar.gz outputs/ logs/

# Backup to external location
scp gpt-researcher-backup-*.tar.gz user@server:/backups/
```

### Backup Docker Image
```bash
# Save image
docker save gpt-researcher:latest | gzip > gpt-researcher-image.tar.gz

# Load image on another system
docker load < gpt-researcher-image.tar.gz
```

## Monitoring

### Resource Usage
```bash
# Real-time stats
docker stats gpt-researcher-pi

# Temperature monitoring
watch -n 2 vcgencmd measure_temp

# Detailed system info
htop
```

### Health Checks
```bash
# Check container health
docker inspect gpt-researcher-pi --format='{{.State.Health.Status}}'

# View health check logs
docker inspect gpt-researcher-pi | grep -A 20 "Health"
```

## Comparison: Docker vs Native

| Aspect | Docker | Native |
|--------|--------|--------|
| **Setup Time** | 5-10 min | 15-30 min |
| **Complexity** | Simple | Medium |
| **Performance** | 5-10% overhead | Best |
| **Updates** | Easy rebuild | Manual |
| **Isolation** | Isolated | System-wide |
| **Portability** | High | Medium |
| **Recommended For** | Most users | Advanced users |

## Multi-Architecture Support

The Dockerfiles work on:
- ✅ Raspberry Pi (ARM64)
- ✅ Intel/AMD Linux (x86_64)
- ✅ Intel Mac (x86_64)
- ✅ Apple Silicon Mac (ARM64)

To build for specific architecture:
```bash
# Build for ARM64 only
docker buildx build --platform linux/arm64 -t gpt-researcher:arm64 .

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t gpt-researcher:latest .
```

## Support

### Check Logs First
```bash
docker-compose -f docker-compose.raspberry-pi.yml logs -f
```

### Common Issues
- Out of memory → Increase swap or reduce resource limits
- Slow performance → Use local LLM, reduce iterations
- Build errors → Check internet connection, try `--no-cache`
- Container crashes → Check logs, verify .env file

### Get Help
- GitHub Issues: https://github.com/assafelovic/gpt-researcher/issues
- Discord: https://discord.gg/spBgZmm3Xe
- Documentation: https://docs.gptr.dev/

---

Made with ❤️ for the Raspberry Pi Docker community :-)

**Pro Tips**:
1. Use SSD instead of SD card for better performance
2. Enable active cooling
3. Use wired ethernet for stability
4. Monitor temperature (`vcgencmd measure_temp`)
5. Regular backups of outputs/
6. Use Ollama for privacy and cost savings

