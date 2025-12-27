#!/bin/bash
# Quick Start Script for CRM SAAS Docker (WSL/Linux)

# Get the script directory and navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "Starting CRM SAAS Docker containers..."
echo "Port: 8016"
echo ""

docker compose up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Containers started successfully!"
    echo ""
    echo "Access URLs:"
    echo "  Application: http://localhost:8016"
    echo "  API Docs:    http://localhost:8016/docs"
    echo "  Health:      http://localhost:8016/health"
else
    echo ""
    echo "✗ Failed to start containers!"
    exit 1
fi

