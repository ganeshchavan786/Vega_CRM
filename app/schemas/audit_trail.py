"""
Audit Trail Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AuditTrailBase(BaseModel):
    """Base audit trail schema"""
    action: str = Field(..., description="Action type: CREATE, UPDATE, DELETE, LOGIN, etc.")
    resource_type: str = Field(..., description="Resource type: Customer, Lead, Deal, etc.")
    resource_id: Optional[int] = Field(None, description="ID of affected resource")
    message: Optional[str] = Field(None, description="Human-readable description")


class AuditTrailResponse(BaseModel):
    """Audit trail response schema"""
    id: int
    timestamp: datetime
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class AuditTrailListResponse(BaseModel):
    """Audit trail list response"""
    audit_trails: List[AuditTrailResponse]
    total: int
    page: int = 1
    per_page: int = 50


class ResourceHistoryResponse(BaseModel):
    """Resource history response"""
    resource_type: str
    resource_id: int
    history: List[AuditTrailResponse]
    total: int


class UserActivityResponse(BaseModel):
    """User activity response"""
    user_id: int
    activities: List[AuditTrailResponse]
    total: int
