#!/bin/bash
# VEGA CRM - SSL Deployment Script (Automatic HTTPS)
# Usage: curl -sSL https://raw.githubusercontent.com/ganeshchavan786/Vega_CRM/main/deploy-ssl.sh | bash -s your-domain.com your-email@example.com

set -e

DOMAIN=$1
EMAIL=$2

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "❌ Usage: ./deploy-ssl.sh your-domain.com your-email@example.com"
    echo ""
    echo "Example:"
    echo "  ./deploy-ssl.sh crm.mycompany.com admin@mycompany.com"
    exit 1
fi

echo "🚀 VEGA CRM SSL Deployment Starting..."
echo "======================================="
echo "Domain: $DOMAIN"
echo "Email:  $EMAIL"
echo ""

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

# Download docker-compose.ssl.yml
echo -e "${BLUE}📥 Downloading SSL configuration...${NC}"
sudo curl -sSL https://raw.githubusercontent.com/ganeshchavan786/Vega_CRM/main/docker-compose.ssl.yml -o docker-compose.yml

# Create .env file
echo -e "${BLUE}⚙️ Creating environment file...${NC}"
sudo tee .env > /dev/null << EOF
# VEGA CRM SSL Configuration
DOMAIN=$DOMAIN
SSL_EMAIL=$EMAIL
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./data/crm.db
ENVIRONMENT=production
EOF
echo -e "${GREEN}✅ Environment file created${NC}"

# Create data directory
sudo mkdir -p data

# Stop any existing containers
sudo docker-compose down 2>/dev/null || true

# Pull and start containers
echo -e "${BLUE}🐳 Pulling Docker images...${NC}"
sudo docker-compose pull

echo -e "${BLUE}🚀 Starting VEGA CRM with SSL...${NC}"
sudo docker-compose up -d

# Wait for startup
echo -e "${BLUE}⏳ Waiting for SSL certificate...${NC}"
sleep 15

# Check status
if sudo docker-compose ps | grep -q "Up"; then
    echo ""
    echo -e "${GREEN}============================================"
    echo "🎉 VEGA CRM with SSL Successfully Deployed!"
    echo "============================================${NC}"
    echo ""
    echo "🔒 Access your CRM at:"
    echo "   https://$DOMAIN"
    echo ""
    echo "📋 Useful Commands:"
    echo "   View logs:    cd $APP_DIR && sudo docker-compose logs -f"
    echo "   Stop:         cd $APP_DIR && sudo docker-compose down"
    echo "   Restart:      cd $APP_DIR && sudo docker-compose restart"
    echo "   Update:       cd $APP_DIR && sudo docker-compose pull && sudo docker-compose up -d"
    echo ""
    echo "⚠️  Note: SSL certificate may take 1-2 minutes to activate."
    echo ""
else
    echo "❌ Deployment failed. Check logs with: sudo docker-compose logs"
    exit 1
fi
