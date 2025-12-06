#!/bin/bash
set -e

# Replace localhost with host.docker.internal in .env file for Docker networking
if [ -f /app/.env ]; then
    echo "Processing .env file for Docker networking..."

    # Create a temporary file with localhost replaced and proper formatting
    # Remove spaces around = signs and replace localhost
    sed 's/localhost/host.docker.internal/g' /app/.env | \
    sed 's/ *= */=/g' > /app/.env.docker

    # Export all variables from the modified .env file
    set -a
    source /app/.env.docker 2>/dev/null || true
    set +a

    echo "Environment variables loaded with host.docker.internal"
    echo "  OPENAI_BASE_URL: ${OPENAI_BASE_URL}"
    echo "  FIRECRAWL_SERVER_URL: ${FIRECRAWL_SERVER_URL}"
else
    echo "Warning: .env file not found, using environment variables from docker-compose"
fi

# Execute the main command
exec "$@"
