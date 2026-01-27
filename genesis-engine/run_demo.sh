#!/bin/bash
# Helper script to run Genesis demo with correct Python

echo "Starting Genesis Engine Demo..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker is not running!"
    echo "Please start Docker Desktop first."
    echo ""
    read -p "Press Enter once Docker is running, or Ctrl+C to exit..."
fi

# Check if services are running
if ! docker ps | grep -q milvus-standalone; then
    echo "📦 Starting services..."
    cd docker && docker compose up -d && cd ..
    echo ""
    echo "⏳ Waiting for services to be ready (10 seconds)..."
    sleep 10
fi

# Run the demo with correct Python
echo "🚀 Launching Genesis Engine..."
echo ""
python3 examples/genesis_demo.py
