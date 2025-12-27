#!/bin/bash
# Stop Script for CRM SAAS Docker (WSL/Linux)

# Get the script directory and navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "Stopping CRM SAAS Docker containers..."
docker compose stop

if [ $? -eq 0 ]; then
    echo "✓ Containers stopped successfully!"
else
    echo "✗ Failed to stop containers!"
    exit 1
fi

