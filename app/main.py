"""
FastAPI Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.routes import auth, company, user, customer, contact, lead, deal, task, activity, email_sequence

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

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - Health check"""
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

