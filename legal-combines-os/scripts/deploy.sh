#!/bin/bash
# scripts/deploy.sh
# Deployment script for Legal Combines OS

set -e

echo "🚀 Starting Legal Combines OS Deployment..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Check .env file
if [ ! -f .env ]; then
    echo "❌ .env file not found. Create from .env.example"
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down || true

# Pull latest code
echo "📦 Pulling latest..."
docker-compose pull

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services
echo "⏳ Waiting for services..."
sleep 10

# Check health
echo "🏥 Checking health..."
curl -f http://localhost:8000/health && echo "✅ Backend healthy" || echo "⚠️ Backend check failed"
curl -f http://localhost:3000 && echo "✅ Frontend accessible" || echo "⚠️ Frontend check failed"

echo "✅ Deployment complete!"
echo "📝 Access:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
