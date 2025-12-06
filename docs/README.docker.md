# Docker Setup Guide :-)

Quick reference for running GPT Researcher with Docker on any platform.

## Quick Start

### Raspberry Pi
```bash
# One-command setup
./docker-start-pi.sh
```

Or manually:
```bash
docker-compose -f docker-compose.raspberry-pi.yml up -d
```

### Linux / Windows / Mac (x86/AMD64)
```bash
docker-compose up -d
```

## What's Included

✅ **All features working**:
- Chat feature (fixed)
- PDF generation (WeasyPrint included)
- All output formats (PDF, DOCX, MD, JSON)
- Health checks
- Auto-restart
- Log management

✅ **Multi-architecture support**:
- ARM64 (Raspberry Pi, Apple Silicon)
- AMD64 (Intel/AMD Linux, Windows, Intel Mac)

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Main image (backend only) |
| `Dockerfile.fullstack` | Full stack (backend + Next.js frontend) |
| `docker-compose.yml` | Standard systems (x86/AMD64) |
| `docker-compose.raspberry-pi.yml` | Raspberry Pi optimized |
| `docker-start-pi.sh` | Automated Pi setup |
| `.dockerignore` | Excludes unnecessary files |
| `DOCKER_RASPBERRY_PI.md` | Complete Pi documentation |

## Common Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build

# Shell access
docker exec -it gpt-researcher bash

# Check status
docker-compose ps

# Resource usage
docker stats
```

## Environment Variables

Create `.env` file:
```bash
# Required
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here

# Optional
LLM_PROVIDER=openai
FAST_LLM_MODEL=gpt-4o-mini
SMART_LLM_MODEL=gpt-4o
MAX_ITERATIONS=4
```

## Ports

- `8000` - Main API and static frontend
- `3000` - Next.js frontend (fullstack only)
- `11434` - Ollama (if using local LLM)

## Volumes

Data persists in:
- `./outputs` - Research reports
- `./logs` - Application logs

## Troubleshooting

### Build fails
```bash
docker-compose build --no-cache
```

### Container exits
```bash
docker-compose logs
```

### Out of memory (Raspberry Pi)
Edit `docker-compose.raspberry-pi.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 1G  # Reduce if needed
```

## Platform-Specific Docs

- **Raspberry Pi**: See `DOCKER_RASPBERRY_PI.md`
- **Native install**: See `RASPBERRY_PI_SETUP.md`

## Support

- Issues: https://github.com/assafelovic/gpt-researcher/issues
- Discord: https://discord.gg/spBgZmm3Xe
- Docs: https://docs.gptr.dev/

