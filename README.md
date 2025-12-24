# 🚀 Vega CRM - Enterprise Customer Relationship Management

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

A modern, enterprise-grade Customer Relationship Management (CRM) system built with FastAPI, featuring lead management, sales pipeline, task tracking, and comprehensive automation.

## ✨ Features

### 🎯 Core CRM Features
- ✅ **Multi-tenant Architecture** - Company-level data isolation
- ✅ **Lead Management** - Complete lead lifecycle with scoring & qualification
- ✅ **Account & Contact Management** - Enterprise account model
- ✅ **Sales Pipeline** - Deal tracking with stages & probability
- ✅ **Task & Activity Management** - Comprehensive activity logging
- ✅ **Email Sequences** - Automated drip campaigns
- ✅ **Lead Conversion** - One-click Lead → Account → Contact → Opportunity
- ✅ **Duplicate Detection** - Smart duplicate lead detection
- ✅ **Assignment Rules** - Automated lead assignment
- ✅ **BANT/MEDDICC Qualification** - Enterprise qualification framework

### 🔐 Security & Authentication
- JWT-based secure authentication
- Role-based access control (RBAC)
- Bcrypt password hashing
- Company-level data isolation

### 📊 Modern UI
- Subscription SaaS-style design
- Dark mode support
- Responsive mobile design
- Real-time updates

## 🛠️ Technology Stack

- **Backend:** FastAPI (Python 3.8+)
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Database:** SQLite (Production: PostgreSQL ready)
- **Architecture:** MVC (Model-View-Controller)
- **Authentication:** JWT (JSON Web Tokens)
- **Validation:** Pydantic
- **Container:** Docker + GitHub Container Registry (GHCR)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Pull from GHCR
docker pull ghcr.io/ganeshchavan786/vega_crm:latest

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  --name vega-crm \
  ghcr.io/ganeshchavan786/vega_crm:latest
```

### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/ganeshchavan786/Vega_CRM.git
cd Vega_CRM

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn app.main:app --reload

# Run frontend (in another terminal)
cd frontend
python -m http.server 8080
```

## 📦 Docker Image

### GitHub Container Registry (GHCR)

We use **GitHub Container Registry** for free, unlimited Docker image hosting:

```bash
# Pull latest image
docker pull ghcr.io/ganeshchavan786/vega_crm:latest

# Pull specific version
docker pull ghcr.io/ganeshchavan786/vega_crm:v1.0.0
```

### Build Locally

```bash
# Build Docker image
docker build -t vega-crm:latest .

# Run container
docker run -d -p 8000:8000 vega-crm:latest
```

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## 🔑 Default Credentials

**Development:**
- Email: `admin@crm.com`
- Password: `Admin@123`

⚠️ **Change these in production!**

## 📁 Project Structure

```
Vega_CRM/
│
├── app/                    # Backend application
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── controllers/       # Business logic
│   ├── routes/            # API endpoints
│   └── utils/             # Utilities
│
├── frontend/               # Frontend application
│   ├── index.html         # Main entry point
│   ├── pages/             # Page components
│   ├── components/       # Reusable components
│   ├── js/                # JavaScript files
│   └── styles.css        # Styling
│
├── guides/                 # User guides
├── Requirements/          # Documentation
├── Dockerfile             # Docker configuration
├── .github/               # GitHub Actions workflows
└── requirements.txt       # Python dependencies
```

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Leads
- `GET /api/companies/{company_id}/leads` - List leads
- `POST /api/companies/{company_id}/leads` - Create lead
- `POST /api/companies/{company_id}/leads/{lead_id}/convert` - Convert lead

### Customers (Accounts)
- `GET /api/companies/{company_id}/customers` - List customers
- `POST /api/companies/{company_id}/customers` - Create customer

### Deals
- `GET /api/companies/{company_id}/deals` - List deals
- `POST /api/companies/{company_id}/deals` - Create deal

### Tasks & Activities
- `GET /api/companies/{company_id}/tasks` - List tasks
- `GET /api/companies/{company_id}/activities` - List activities

## 🧪 Testing

```bash
# Run comprehensive test suite
python test_all_forms_debug.py

# Run API tests
pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- All contributors and users of Vega CRM

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/ganeshchavan786/Vega_CRM/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ganeshchavan786/Vega_CRM/discussions)

---

**Made with ❤️ by the Vega CRM Team**

**Version:** 1.0.0  
**Last Updated:** December 24, 2025
