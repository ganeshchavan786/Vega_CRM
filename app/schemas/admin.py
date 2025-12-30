"""
Admin Schemas - Email Settings, System Settings
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# Email Settings Schemas
class EmailSettingsBase(BaseModel):
    """Base email settings schema"""
    smtp_host: str = Field(..., description="SMTP server host")
    smtp_port: int = Field(587, description="SMTP server port")
    smtp_username: str = Field(..., description="SMTP username")
    smtp_from_email: EmailStr = Field(..., description="From email address")
    smtp_from_name: str = Field("Vega CRM", description="From name")
    smtp_use_tls: bool = Field(True, description="Use TLS")


class EmailSettingsCreate(EmailSettingsBase):
    """Email settings create schema"""
    smtp_password: str = Field(..., description="SMTP password")


class EmailSettingsUpdate(BaseModel):
    """Email settings update schema"""
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[EmailStr] = None
    smtp_from_name: Optional[str] = None
    smtp_use_tls: Optional[bool] = None


class EmailSettingsResponse(BaseModel):
    """Email settings response (password masked)"""
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_from_email: str
    smtp_from_name: str
    smtp_use_tls: bool
    is_configured: bool


class TestEmailRequest(BaseModel):
    """Test email request schema"""
    to_email: EmailStr = Field(..., description="Email address to send test to")


class TestEmailResponse(BaseModel):
    """Test email response schema"""
    success: bool
    message: str


# Email Provider Schemas
class EmailProviderInfo(BaseModel):
    """Email provider info"""
    name: str
    smtp_host: str
    smtp_port: int
    use_tls: bool
    description: str


class EmailProvidersResponse(BaseModel):
    """Email providers list response"""
    providers: List[EmailProviderInfo]


# System Settings Schemas
class SystemStatsResponse(BaseModel):
    """System statistics response"""
    total_users: int
    total_companies: int
    total_customers: int
    total_leads: int
    total_deals: int
    total_tasks: int
    total_activities: int
    database_size: Optional[str] = None
    uptime: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """System health response"""
    status: str
    database: str
    email_service: str
    timestamp: datetime


class BackgroundJobInfo(BaseModel):
    """Background job info"""
    id: str
    name: str
    status: str
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    description: Optional[str] = None


class BackgroundJobsResponse(BaseModel):
    """Background jobs list response"""
    jobs: List[BackgroundJobInfo]
    total: int
