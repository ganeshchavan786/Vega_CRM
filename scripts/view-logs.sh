#!/bin/bash
# View Logs Script for CRM SAAS Docker (WSL/Linux)

# Get the script directory and navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "Viewing CRM SAAS Docker logs (Press Ctrl+C to exit)..."
echo ""
docker compose logs -f

