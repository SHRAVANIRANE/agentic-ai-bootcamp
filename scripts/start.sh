#!/bin/bash
set -e

echo "🚀 Starting Inventory Demand Forecasting Agent..."

# Pull Llama 3 model into Ollama container
echo "📥 Pulling Llama 3 model (first run only)..."
docker compose up -d ollama
sleep 5
docker compose exec ollama ollama pull llama3

# Start full stack
echo "🏗️  Building and starting all services..."
docker compose up --build -d

echo ""
echo "✅ System is running:"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Frontend:     http://localhost:3000"
echo "   Ollama:       http://localhost:11434"
echo ""
echo "📋 Quick test:"
echo "   curl http://localhost:8000/health"
