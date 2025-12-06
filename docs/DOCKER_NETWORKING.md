# Docker Networking Configuration

## Overview
The GPT Researcher Docker container is configured to automatically connect to other Docker containers running on your host machine (like LiteLLM and Firecrawl).

## How It Works

### Automatic localhost → host.docker.internal Replacement
When the container starts, the `docker-entrypoint.sh` script automatically:
1. Reads your `.env` file
2. Replaces all `localhost` references with `host.docker.internal`
3. Loads the modified environment variables
4. Starts the application

### What Gets Replaced
Your `.env` file contains:
```bash
OPENAI_BASE_URL="http://localhost:4000/v1"
FIRECRAWL_SERVER_URL="http://localhost:3002"
```

Inside the container, these become:
```bash
OPENAI_BASE_URL="http://host.docker.internal:4000/v1"
FIRECRAWL_SERVER_URL="http://host.docker.internal:3002"
```

## Configuration Files

### 1. docker-entrypoint.sh
**Purpose**: Entrypoint script that processes `.env` file and replaces localhost

**Key Features**:
- Replaces `localhost` with `host.docker.internal`
- Removes spaces around `=` signs for proper bash parsing
- Exports all environment variables
- Shows loaded URLs in logs for verification

**Location**: `/docker-entrypoint.sh`

### 2. Dockerfile
**Changes**:
- Copies entrypoint script to `/usr/local/bin/`
- Makes script executable
- Sets as container ENTRYPOINT

**Lines**:
```dockerfile
# Copy and set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set entrypoint and default command
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. docker-compose.yml
**Changes**:
- Added `extra_hosts` to ensure `host.docker.internal` resolves correctly on all platforms

**Lines**:
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## Verification

### Check Logs
When the container starts, you'll see:
```bash
$ docker compose logs

gpt-researcher  | Processing .env file for Docker networking...
gpt-researcher  | Environment variables loaded with host.docker.internal
gpt-researcher  |   OPENAI_BASE_URL: http://host.docker.internal:4000/v1
gpt-researcher  |   FIRECRAWL_SERVER_URL: http://host.docker.internal:3002
gpt-researcher  | INFO:     Started server process [1]
gpt-researcher  | INFO:     Application startup complete.
```

### Manual Test
You can exec into the container to verify:
```bash
# Enter the container
docker compose exec gpt-researcher bash

# Check environment variables
echo $OPENAI_BASE_URL
# Output: http://host.docker.internal:4000/v1

echo $FIRECRAWL_SERVER_URL
# Output: http://host.docker.internal:3002

# Check .env.docker file
cat /app/.env.docker
```

## How to Use

### 1. Start Your Other Services
Make sure your LiteLLM and Firecrawl containers are running:
```bash
# Check running containers
docker ps

# You should see:
# - LiteLLM on port 4000
# - Firecrawl on port 3002
```

### 2. Start GPT Researcher
```bash
docker compose up -d
```

### 3. Verify Connection
Check logs to confirm the URLs were replaced:
```bash
docker compose logs | grep "host.docker.internal"
```

## Supported Services

This configuration automatically works with any service running on your host machine via Docker:

### LiteLLM (OpenAI Proxy)
- **Your .env**: `OPENAI_BASE_URL="http://localhost:4000/v1"`
- **Container sees**: `http://host.docker.internal:4000/v1`
- **Purpose**: Unified LLM API gateway

### Firecrawl (Web Scraping)
- **Your .env**: `FIRECRAWL_SERVER_URL="http://localhost:3002"`
- **Container sees**: `http://host.docker.internal:3002`
- **Purpose**: Web content extraction

### Any Other Service
The script replaces **ALL** `localhost` references, so any service running on your host is automatically accessible:
- Redis: `redis://localhost:6379` → `redis://host.docker.internal:6379`
- PostgreSQL: `localhost:5432` → `host.docker.internal:5432`
- Etc.

## Platform Compatibility

### macOS
✅ Fully supported via `host.docker.internal` (built-in)

### Linux
✅ Supported via `extra_hosts` configuration in docker-compose.yml:
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

### Windows (Docker Desktop)
✅ Fully supported via `host.docker.internal` (built-in)

## Troubleshooting

### Issue: Container can't connect to host services

**Check 1**: Verify services are running on host
```bash
# Test from host machine
curl http://localhost:4000/v1/models  # LiteLLM
curl http://localhost:3002/health     # Firecrawl
```

**Check 2**: Verify URLs in container logs
```bash
docker compose logs | grep "OPENAI_BASE_URL\|FIRECRAWL_SERVER_URL"
```

**Check 3**: Test from inside container
```bash
docker compose exec gpt-researcher bash
curl http://host.docker.internal:4000/v1/models
```

### Issue: Environment variables not loaded

**Solution**: Check .env file format
- Ensure no syntax errors
- Script handles spaces around `=` automatically
- Check for quote issues

**Debug**:
```bash
docker compose exec gpt-researcher cat /app/.env.docker
```

### Issue: host.docker.internal not resolving (Linux)

**Solution**: Ensure `extra_hosts` is in docker-compose.yml:
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## Technical Details

### Why host.docker.internal?
- Docker networking isolates containers from the host
- `localhost` inside a container refers to the container itself, not the host
- `host.docker.internal` is a special DNS name that resolves to the host machine's IP
- Supported across all platforms (macOS, Windows, Linux with extra_hosts)

### Environment Variable Loading
The entrypoint script uses bash's `source` command to load variables:
```bash
set -a                      # Auto-export all variables
source /app/.env.docker     # Load from file
set +a                      # Disable auto-export
```

### Security Considerations
- Original `.env` file remains unchanged (mounted read-only)
- Modified `.env.docker` only exists inside the container
- No credentials are exposed in logs (only URLs are printed)
- Script uses `2>/dev/null || true` to suppress errors gracefully

## Best Practices

### 1. Keep .env File Clean
Your `.env` should always use `localhost` for local development:
```bash
OPENAI_BASE_URL="http://localhost:4000/v1"  # Good
OPENAI_BASE_URL="http://host.docker.internal:4000/v1"  # Don't do this
```

The entrypoint script handles the conversion automatically.

### 2. Use Standard Ports
Stick to predictable port numbers:
- LiteLLM: 4000
- Firecrawl: 3002
- Redis: 6379
- PostgreSQL: 5432

### 3. Check Logs on Startup
Always verify the URLs were replaced correctly:
```bash
docker compose up -d && docker compose logs | grep "host.docker.internal"
```

### 4. Use docker compose
Prefer `docker compose` over `docker run` to ensure `extra_hosts` configuration is applied.

## Summary

### What Was Added
- ✅ `docker-entrypoint.sh` - Automatic localhost replacement
- ✅ `extra_hosts` in docker-compose.yml - Linux compatibility
- ✅ ENTRYPOINT in Dockerfile - Runs script on startup

### What It Does
- 🔄 Automatically converts `localhost` → `host.docker.internal`
- 🔄 Fixes .env formatting (spaces around `=`)
- 📝 Logs loaded URLs for verification
- ✅ Works on all platforms (macOS, Linux, Windows)

### Result
**Your GPT Researcher container can now seamlessly connect to LiteLLM, Firecrawl, and any other services running on your host machine!**

---

**Date**: 2025-12-05
**Status**: ✅ Implemented and Tested
**Platform Support**: macOS, Linux, Windows
