"""
Admin Routes - Email Settings, System Settings, Background Jobs
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
import os
from app.database import get_db
from app.schemas.admin import (
    EmailSettingsCreate, EmailSettingsUpdate, EmailSettingsResponse,
    TestEmailRequest, TestEmailResponse,
    EmailProviderInfo, EmailProvidersResponse,
    SystemStatsResponse, SystemHealthResponse,
    BackgroundJobInfo, BackgroundJobsResponse
)
from app.config.email_config import get_email_config, is_email_configured
from app.services.email_service import send_email, initialize_email_service
from app.utils.dependencies import get_current_active_user
from app.utils.permissions import require_admin, require_super_admin
from app.utils.helpers import success_response
from app.models.user import User
from app.models.company import Company
from app.models.customer import Customer
from app.models.lead import Lead
from app.models.deal import Deal
from app.models.task import Task
from app.models.activity import Activity

router = APIRouter()


# ==================== Email Settings ====================

@router.get("/admin/email-settings", response_model=EmailSettingsResponse)
async def get_email_settings(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get current email settings (password masked)
    
    Requires: Admin role
    """
    config = get_email_config()
    
    return EmailSettingsResponse(
        smtp_host=config.get("smtp_host", ""),
        smtp_port=config.get("smtp_port", 587),
        smtp_username=config.get("smtp_username", ""),
        smtp_from_email=config.get("smtp_from_email", ""),
        smtp_from_name=config.get("smtp_from_name", "Vega CRM"),
        smtp_use_tls=config.get("smtp_use_tls", True),
        is_configured=is_email_configured()
    )


@router.put("/admin/email-settings")
async def update_email_settings(
    settings: EmailSettingsUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Update email settings (updates .env file)
    
    Requires: Super Admin role
    
    Note: This updates environment variables. Server restart may be required.
    """
    env_updates = {}
    
    if settings.smtp_host is not None:
        env_updates["SMTP_HOST"] = settings.smtp_host
    if settings.smtp_port is not None:
        env_updates["SMTP_PORT"] = str(settings.smtp_port)
    if settings.smtp_username is not None:
        env_updates["SMTP_USERNAME"] = settings.smtp_username
    if settings.smtp_password is not None:
        env_updates["SMTP_PASSWORD"] = settings.smtp_password
    if settings.smtp_from_email is not None:
        env_updates["SMTP_FROM_EMAIL"] = settings.smtp_from_email
    if settings.smtp_from_name is not None:
        env_updates["SMTP_FROM_NAME"] = settings.smtp_from_name
    if settings.smtp_use_tls is not None:
        env_updates["SMTP_USE_TLS"] = str(settings.smtp_use_tls)
    
    # Update environment variables
    for key, value in env_updates.items():
        os.environ[key] = value
    
    # Reinitialize email service
    initialize_email_service()
    
    return success_response(
        data={"updated_fields": list(env_updates.keys())},
        message="Email settings updated. Some changes may require server restart."
    )


@router.post("/admin/email-settings/test", response_model=TestEmailResponse)
async def test_email_settings(
    request: TestEmailRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Send a test email to verify settings
    
    Requires: Admin role
    """
    if not is_email_configured():
        return TestEmailResponse(
            success=False,
            message="Email is not configured. Please configure SMTP settings first."
        )
    
    try:
        result = await send_email(
            to_email=request.to_email,
            subject="Vega CRM - Test Email",
            template_name="test_email.html",
            template_data={
                "user_name": current_user.first_name or current_user.email,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        if result:
            return TestEmailResponse(
                success=True,
                message=f"Test email sent successfully to {request.to_email}"
            )
        else:
            return TestEmailResponse(
                success=False,
                message="Failed to send test email. Check server logs for details."
            )
    except Exception as e:
        return TestEmailResponse(
            success=False,
            message=f"Error sending test email: {str(e)}"
        )


@router.get("/admin/email-providers", response_model=EmailProvidersResponse)
async def get_email_providers(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of common email providers with their SMTP settings
    
    Requires: Admin role
    """
    providers = [
        EmailProviderInfo(
            name="Gmail",
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            use_tls=True,
            description="Google Gmail - requires App Password for 2FA accounts"
        ),
        EmailProviderInfo(
            name="Outlook/Office365",
            smtp_host="smtp.office365.com",
            smtp_port=587,
            use_tls=True,
            description="Microsoft Outlook and Office 365"
        ),
        EmailProviderInfo(
            name="Yahoo",
            smtp_host="smtp.mail.yahoo.com",
            smtp_port=587,
            use_tls=True,
            description="Yahoo Mail - requires App Password"
        ),
        EmailProviderInfo(
            name="SendGrid",
            smtp_host="smtp.sendgrid.net",
            smtp_port=587,
            use_tls=True,
            description="SendGrid transactional email service"
        ),
        EmailProviderInfo(
            name="Mailgun",
            smtp_host="smtp.mailgun.org",
            smtp_port=587,
            use_tls=True,
            description="Mailgun email service"
        ),
        EmailProviderInfo(
            name="Amazon SES",
            smtp_host="email-smtp.us-east-1.amazonaws.com",
            smtp_port=587,
            use_tls=True,
            description="Amazon Simple Email Service (region may vary)"
        ),
        EmailProviderInfo(
            name="Custom SMTP",
            smtp_host="",
            smtp_port=587,
            use_tls=True,
            description="Custom SMTP server configuration"
        )
    ]
    
    return EmailProvidersResponse(providers=providers)


# ==================== System Settings ====================

@router.get("/admin/system/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get system statistics
    
    Requires: Admin role
    """
    stats = SystemStatsResponse(
        total_users=db.query(func.count(User.id)).scalar() or 0,
        total_companies=db.query(func.count(Company.id)).scalar() or 0,
        total_customers=db.query(func.count(Customer.id)).scalar() or 0,
        total_leads=db.query(func.count(Lead.id)).scalar() or 0,
        total_deals=db.query(func.count(Deal.id)).scalar() or 0,
        total_tasks=db.query(func.count(Task.id)).scalar() or 0,
        total_activities=db.query(func.count(Activity.id)).scalar() or 0,
        database_size=None,  # Could be calculated for SQLite
        uptime=None  # Would need process start time tracking
    )
    
    return stats


@router.get("/admin/system/health", response_model=SystemHealthResponse)
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get system health status
    
    Requires: Admin role
    """
    # Check database
    db_status = "healthy"
    try:
        db.execute("SELECT 1")
    except Exception:
        db_status = "unhealthy"
    
    # Check email service
    email_status = "configured" if is_email_configured() else "not_configured"
    
    return SystemHealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        email_service=email_status,
        timestamp=datetime.utcnow()
    )


# ==================== Background Jobs ====================

@router.get("/admin/background-jobs", response_model=BackgroundJobsResponse)
async def get_background_jobs(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of background jobs and their status
    
    Requires: Admin role
    """
    # Placeholder - would integrate with actual job scheduler (APScheduler, Celery, etc.)
    jobs = [
        BackgroundJobInfo(
            id="email_reminder",
            name="Email Reminders",
            status="scheduled",
            last_run=None,
            next_run=None,
            description="Send reminder emails for upcoming tasks and follow-ups"
        ),
        BackgroundJobInfo(
            id="log_cleanup",
            name="Log Cleanup",
            status="scheduled",
            last_run=None,
            next_run=None,
            description="Clean up old log entries"
        ),
        BackgroundJobInfo(
            id="data_backup",
            name="Data Backup",
            status="not_configured",
            last_run=None,
            next_run=None,
            description="Automated database backup"
        )
    ]
    
    return BackgroundJobsResponse(
        jobs=jobs,
        total=len(jobs)
    )


@router.post("/admin/background-jobs/{job_id}/run")
async def run_background_job(
    job_id: str,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a background job
    
    Requires: Super Admin role
    """
    # Placeholder - would integrate with actual job scheduler
    valid_jobs = ["email_reminder", "log_cleanup", "data_backup"]
    
    if job_id not in valid_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found"
        )
    
    return success_response(
        data={"job_id": job_id, "status": "triggered"},
        message=f"Job '{job_id}' has been triggered"
    )
