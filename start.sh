#!/bin/bash

# CRM SAAS - One Click Start Script
# Run this in WSL: ./start.sh

echo "🚀 Starting CRM SAAS..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker is not running. Starting Docker..."
    sudo service docker start
    sleep 3
fi

# Build and start containers
echo "📦 Building and starting containers..."
docker-compose up --build -d

# Wait for container to be healthy
echo "⏳ Waiting for application to start..."
sleep 5

# Check if container is running
if docker ps | grep -q crm-saas; then
    echo ""
    echo "✅ CRM SAAS is running!"
    echo ""
    echo "🌐 Open in browser: http://localhost:8000"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs:    docker-compose logs -f"
    echo "   Stop:         docker-compose down"
    echo "   Restart:      docker-compose restart"
    echo ""
else
    echo "❌ Failed to start. Check logs:"
    docker-compose logs
fi
