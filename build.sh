#!/bin/bash
# Build script for Docker deployment

# Clean up old containers and images
docker compose down

# Build fresh images
docker compose build --no-cache

# Start services
docker compose up -d

echo "Build complete! Services are starting..."
echo "Backend will be available at: http://localhost:${BACKEND_PORT:-8000}"
echo "Frontend will be available at: http://localhost:${FRONTEND_PORT:-8501}"
