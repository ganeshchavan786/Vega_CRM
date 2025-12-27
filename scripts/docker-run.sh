#!/bin/bash
# Docker Commands Script for CRM SAAS (WSL/Linux)
# This script works in WSL bash

# Get the script directory and navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "========================================"
echo "CRM SAAS - Docker Commands (WSL)"
echo "========================================"
echo ""

# Check if Docker is running
echo "Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running or not accessible!"
    echo "Please start Docker Desktop or ensure Docker is running."
    exit 1
fi
echo "Docker is running ✓"
echo ""

# Function to run docker compose commands (v2 syntax)
run_docker_compose() {
    echo "Running: docker compose $@"
    docker compose "$@"
}

# Menu
echo "Select an option:"
echo "1. Build and start containers"
echo "2. Start containers (if already built)"
echo "3. Stop containers"
echo "4. Restart containers"
echo "5. View logs"
echo "6. Build only (no start)"
echo "7. Stop and remove containers"
echo "8. View container status"
echo ""

read -p "Enter your choice (1-8): " choice

case $choice in
    1)
        echo "Building and starting containers..."
        docker compose up -d --build
        echo ""
        echo "Application will be available at: http://localhost:8016"
        echo "API Docs: http://localhost:8016/docs"
        echo "Health Check: http://localhost:8016/health"
        ;;
    2)
        echo "Starting containers..."
        docker compose up -d
        echo ""
        echo "Application will be available at: http://localhost:8016"
        ;;
    3)
        echo "Stopping containers..."
        docker compose stop
        echo "Containers stopped."
        ;;
    4)
        echo "Restarting containers..."
        docker compose restart
        echo "Containers restarted."
        ;;
    5)
        echo "Viewing logs (Press Ctrl+C to exit)..."
        docker compose logs -f
        ;;
    6)
        echo "Building containers..."
        docker compose build
        echo "Build complete."
        ;;
    7)
        echo "Stopping and removing containers..."
        docker compose down
        echo "Containers stopped and removed."
        ;;
    8)
        echo "Container status:"
        docker ps -a --filter "name=crm-saas"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "Done!"

