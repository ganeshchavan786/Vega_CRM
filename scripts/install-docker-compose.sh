#!/bin/bash
# Install docker-compose (v1) for WSL/Linux

echo "Installing docker-compose..."

# Check if docker-compose is already installed
if command -v docker-compose &> /dev/null; then
    echo "docker-compose is already installed!"
    docker-compose --version
    exit 0
fi

# Install docker-compose
echo "Installing docker-compose using apt..."
sudo apt update
sudo apt install -y docker-compose

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ docker-compose installed successfully!"
    docker-compose --version
else
    echo ""
    echo "✗ Failed to install docker-compose!"
    echo ""
    echo "Alternative: Use 'docker compose' (v2) instead of 'docker-compose'"
    echo "If you have Docker Desktop, it includes 'docker compose' plugin"
    exit 1
fi

