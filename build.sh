#!/bin/bash
# Build script for x86_64 architecture

export DOCKER_DEFAULT_PLATFORM=linux/amd64

# Clean up old containers and images
docker compose down

# Build with platform specification
docker compose build --no-cache

# Start services
docker compose up -d

echo "Build complete! Services are starting..."
echo "Backend will be available at: http://localhost:${BACKEND_PORT:-8000}"
echo "Frontend will be available at: http://localhost:${FRONTEND_PORT:-8501}"
