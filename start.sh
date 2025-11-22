#!/bin/bash

echo "🚀 Starting Multimodal Retrieval System..."

# Start backend services
echo "🔨 Building and starting backend..."
docker-compose up -d --build

echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "✅ Backend started!"
echo ""
echo "🌐 Access Points:"
echo "   - Backend API:    http://localhost:8000"
echo "   - API Docs:       http://localhost:8000/docs"
echo "   - Qdrant:         http://localhost:6333/dashboard"
echo ""
echo "💡 Start frontend separately:"
echo "   cd frontend && npm run dev"
echo ""
