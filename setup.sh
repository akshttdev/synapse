#!/bin/bash

echo "🚀 Setting up Multimodal Retrieval System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build images
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🏥 Checking service health..."
curl -s http://localhost:8000/health || echo "Backend not ready yet"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Access points:"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:3000"
echo "   - Qdrant: http://localhost:6333/dashboard"
echo "   - MinIO Console: http://localhost:9001"
echo ""
echo "📋 To view logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
