"""
Log Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class LogBase(BaseModel):
    """Base log schema"""
    level: str = Field(..., description="Log level: INFO, WARNING, ERROR, DEBUG")
    category: str = Field(..., description="Log category: Auth, Email, Admin, System, Security")
    action: str = Field(..., description="Action performed")
    message: str = Field(..., description="Log message")


class LogCreate(LogBase):
    """Log creation schema"""
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    status: str = "Success"


class LogResponse(BaseModel):
    """Log response schema"""
    id: int
    timestamp: datetime
    level: str
    category: str
    action: str
    message: str
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    status: str

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    """Log list response"""
    logs: List[LogResponse]
    total: int
    page: int = 1
    per_page: int = 50


class LogStatisticsResponse(BaseModel):
    """Log statistics response"""
    total_logs: int
    error_count: int
    warning_count: int
    info_count: int
    auth_logs: int
    email_logs: int
    failed_logins: int
    failed_emails: int
    period_days: int


class LogCleanupResponse(BaseModel):
    """Log cleanup response"""
    deleted_count: int
    message: str
