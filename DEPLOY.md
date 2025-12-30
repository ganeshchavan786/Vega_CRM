# 🚀 VEGA CRM - VPS Deployment Guide

## One Command Deployment (सर्वात सोपे!)

कोणत्याही VPS वर (Ubuntu/Debian/CentOS) हे एक command run करा:

```bash
curl -sSL https://raw.githubusercontent.com/ganeshchavan786/Vega_CRM/main/deploy.sh | bash
```

बस! VEGA CRM automatically install आणि start होईल.

---

## Manual Deployment (Step by Step)

### Step 1: VPS वर SSH Login करा
```bash
ssh root@your-server-ip
```

### Step 2: Docker Install करा
```bash
curl -fsSL https://get.docker.com | sh
```

### Step 3: App Directory बनवा
```bash
mkdir -p /opt/vega-crm
cd /opt/vega-crm
```

### Step 4: Docker Compose File Download करा
```bash
curl -sSL https://raw.githubusercontent.com/ganeshchavan786/Vega_CRM/main/docker-compose.prod.yml -o docker-compose.yml
```

### Step 5: Environment File बनवा
```bash
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./data/crm.db
ENVIRONMENT=production
PORT=8000
EOF
```

### Step 6: Start करा
```bash
docker-compose up -d
```

### Step 7: Access करा
```
http://your-server-ip:8000
```

---

## 📋 Useful Commands

| Command | Description |
|---------|-------------|
| `docker-compose logs -f` | Live logs पहा |
| `docker-compose down` | Stop करा |
| `docker-compose restart` | Restart करा |
| `docker-compose pull && docker-compose up -d` | Update करा |

---

## 🔧 Custom Port वापरायचा असेल

`.env` file मध्ये PORT बदला:
```bash
PORT=80
```

---

## 🔒 SSL/HTTPS Setup (Optional)

Nginx reverse proxy सह SSL:

```bash
# Install Nginx & Certbot
apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
cat > /etc/nginx/sites-available/vega-crm << EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/vega-crm /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Get SSL certificate
certbot --nginx -d your-domain.com
```

---

## 🆘 Troubleshooting

### Container start होत नाही?
```bash
docker-compose logs
```

### Port already in use?
```bash
# Check what's using port 8000
lsof -i :8000

# Change port in .env
PORT=8080
docker-compose up -d
```

### Data backup?
```bash
cp -r /opt/vega-crm/data /backup/vega-crm-backup
```

---

## 📞 Support

- GitHub Issues: https://github.com/ganeshchavan786/Vega_CRM/issues
- Docker Image: `ghcr.io/ganeshchavan786/vega_crm:latest`
