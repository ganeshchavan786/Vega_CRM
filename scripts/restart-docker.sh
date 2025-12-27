#!/bin/bash
# Restart Script for CRM SAAS Docker (WSL/Linux)

# Get the script directory and navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "Restarting CRM SAAS Docker containers..."
docker compose restart

if [ $? -eq 0 ]; then
    echo "✓ Containers restarted successfully!"
    echo ""
    echo "Application available at: http://localhost:8016"
else
    echo "✗ Failed to restart containers!"
    exit 1
fi

