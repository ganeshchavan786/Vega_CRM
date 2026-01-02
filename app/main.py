"""
FastAPI Main Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.database import engine, Base
from app.routes import auth, company, user, customer, contact, lead, deal, task, activity, email_sequence, permission, audit, logs, admin, reports, data_management, nurturing, qualification
import logging
import time

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CRM SAAS Application - Customer Relationship Management System",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================
# VEGA CRM Website - Root Route (must be first)
# ============================================
@app.get("/", include_in_schema=False)
async def serve_vega_website():
    """Serve VEGA CRM Website as homepage"""
    import sys
    
    # Determine base path based on environment
    if getattr(sys, 'frozen', False):
        # PyInstaller EXE
        base_path = sys._MEIPASS
    elif os.path.exists("/app/frontend"):
        # Docker
        base_path = "/app"
    else:
        # Development
        base_path = os.path.dirname(os.path.dirname(__file__))
    
    website_path = os.path.join(base_path, "frontend", "website", "index.html")
    fallback_path = os.path.join(base_path, "frontend", "index.html")
    
    if os.path.exists(website_path):
        return FileResponse(website_path)
    elif os.path.exists(fallback_path):
        return FileResponse(fallback_path)
    return {"message": "Welcome to VEGA CRM API"}

# ============================================
# Security Middleware - Allowed Hosts
# ============================================
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# ============================================
# Request Logging Middleware
# ============================================
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        if settings.DEBUG:
            logger.debug(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(RequestLoggingMiddleware)


# ============================================
# CORS Configuration
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint - Serve frontend if available, else API info
@app.get("/")
async def root():
    """Root endpoint - Serve frontend or API info"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "success": True,
        "message": "CRM SAAS API is running",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "status": "healthy",
        "message": "API is operational"
    }


# Background Tasks Status endpoint
@app.get("/api/system/background-tasks")
async def get_background_tasks_status():
    """Get background tasks queue status"""
    from app.utils.background_tasks import task_manager
    return {
        "success": True,
        "data": task_manager.get_status(),
        "message": "Background tasks status"
    }


# System Info endpoint
@app.get("/api/system/info")
async def get_system_info():
    """Get system configuration info"""
    return {
        "success": True,
        "data": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "workers": settings.WORKERS,
            "background_tasks_enabled": settings.BACKGROUND_TASK_ENABLED,
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED
        },
        "message": "System info"
    }


# Include routers - Phase 1
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(company.router, prefix="/api/companies", tags=["Companies"])
app.include_router(user.router, prefix="/api/companies", tags=["Users"])
app.include_router(customer.router, prefix="/api/companies", tags=["Customers"])
app.include_router(contact.router, prefix="/api/companies", tags=["Contacts"])

# Include routers - Phase 2
app.include_router(lead.router, prefix="/api/companies", tags=["Leads"])
app.include_router(deal.router, prefix="/api/companies", tags=["Deals"])
app.include_router(task.router, prefix="/api/companies", tags=["Tasks"])
app.include_router(activity.router, prefix="/api/companies", tags=["Activities"])
app.include_router(email_sequence.router, prefix="/api/companies", tags=["Email Sequences"])

# Include routers - Security & Admin
app.include_router(permission.router, prefix="/api", tags=["Permissions"])
app.include_router(audit.router, prefix="/api", tags=["Audit Trail"])
app.include_router(logs.router, prefix="/api", tags=["System Logs"])
app.include_router(admin.router, prefix="/api", tags=["Admin Settings"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])

# Include routers - Data Management (Phase 1)
app.include_router(data_management.router, prefix="/api/companies", tags=["Data Management"])

# Include routers - Lead Nurturing (Phase 2)
app.include_router(nurturing.router, prefix="/api/companies", tags=["Lead Nurturing"])

# Include routers - Lead Qualification (Phase 3)
app.include_router(qualification.router, prefix="/api/companies", tags=["Lead Qualification"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all uncaught exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "details": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


# Mount frontend static files
# Check if frontend directory exists (for Docker deployment)
# Use absolute path for Docker compatibility
import sys
if getattr(sys, 'frozen', False):
    # Running as PyInstaller EXE
    base_path = sys._MEIPASS
    frontend_path = os.path.join(base_path, "frontend")
    guides_path = os.path.join(base_path, "guides")
elif os.path.exists("/app/frontend"):
    # Docker deployment
    frontend_path = "/app/frontend"
    guides_path = "/app/guides"
else:
    # Development
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    guides_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "guides")

if os.path.exists(frontend_path):
    # Mount static directories
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    app.mount("/pages", StaticFiles(directory=os.path.join(frontend_path, "pages")), name="pages")
    app.mount("/components", StaticFiles(directory=os.path.join(frontend_path, "components")), name="components")
    
    # Mount VEGA CRM Website
    website_path = os.path.join(frontend_path, "website")
    if os.path.exists(website_path):
        app.mount("/website", StaticFiles(directory=website_path, html=True), name="website")
        logger.info(f"VEGA CRM Website mounted at /website")
    
    # Mount User Guides
    if os.path.exists(guides_path):
        app.mount("/guides", StaticFiles(directory=guides_path, html=True), name="guides")
        logger.info(f"User Guides mounted at /guides")
    
    # Serve CRM App at /app
    @app.get("/app", include_in_schema=False)
    async def serve_crm_app():
        return FileResponse(os.path.join(frontend_path, "index.html"))
    
    # Serve styles.css
    @app.get("/styles.css", include_in_schema=False)
    async def serve_styles():
        return FileResponse(os.path.join(frontend_path, "styles.css"))
    
    logger.info(f"Frontend mounted from: {frontend_path}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

