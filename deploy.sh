#!/bin/bash
# VEGA CRM - One Command VPS Deployment Script
# Usage: curl -sSL https://raw.githubusercontent.com/ganeshchavan786/Vega_CRM/main/deploy.sh | bash

set -e

echo "🚀 VEGA CRM Deployment Starting..."
echo "=================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}📦 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker installed${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}📦 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
fi

# Create app directory
APP_DIR="/opt/vega-crm"
echo -e "${BLUE}📁 Creating app directory: $APP_DIR${NC}"
sudo mkdir -p $APP_DIR
cd $APP_DIR

# Download docker-compose.prod.yml
echo -e "${BLUE}📥 Downloading configuration...${NC}"
sudo curl -sSL https://raw.githubusercontent.com/ganeshchavan786/Vega_CRM/main/docker-compose.prod.yml -o docker-compose.yml

# Create .env file if not exists
if [ ! -f .env ]; then
    echo -e "${BLUE}⚙️ Creating environment file...${NC}"
    cat > .env << EOF
# VEGA CRM Environment Configuration
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./data/crm.db
ENVIRONMENT=production
PORT=8000
EOF
    echo -e "${GREEN}✅ Environment file created${NC}"
fi

# Create data directory
sudo mkdir -p data

# Pull and start containers
echo -e "${BLUE}🐳 Pulling Docker image...${NC}"
sudo docker-compose pull

echo -e "${BLUE}🚀 Starting VEGA CRM...${NC}"
sudo docker-compose up -d

# Wait for startup
sleep 5

# Check status
if sudo docker-compose ps | grep -q "Up"; then
    echo ""
    echo -e "${GREEN}=================================="
    echo "🎉 VEGA CRM Successfully Deployed!"
    echo "==================================${NC}"
    echo ""
    echo "📍 Access your CRM at:"
    echo "   http://$(curl -s ifconfig.me):8000"
    echo "   http://localhost:8000"
    echo ""
    echo "📋 Useful Commands:"
    echo "   View logs:    cd $APP_DIR && sudo docker-compose logs -f"
    echo "   Stop:         cd $APP_DIR && sudo docker-compose down"
    echo "   Restart:      cd $APP_DIR && sudo docker-compose restart"
    echo "   Update:       cd $APP_DIR && sudo docker-compose pull && sudo docker-compose up -d"
    echo ""
else
    echo "❌ Deployment failed. Check logs with: sudo docker-compose logs"
    exit 1
fi
