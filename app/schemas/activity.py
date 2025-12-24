"""
Activity Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ActivityBase(BaseModel):
    """Base activity schema"""
    activity_type: str = Field(..., pattern="^(call|email|meeting|note|status_change)$")
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0)  # Minutes
    outcome: Optional[str] = Field(None, pattern="^(positive|negative|neutral|follow_up_required)$")
    activity_date: datetime


class ActivityCreate(ActivityBase):
    """Create activity schema"""
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    task_id: Optional[int] = None


class ActivityUpdate(BaseModel):
    """Update activity schema - all fields optional"""
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0)
    outcome: Optional[str] = Field(None, pattern="^(positive|negative|neutral|follow_up_required)$")
    activity_date: Optional[datetime] = None


class ActivityResponse(ActivityBase):
    """Activity response schema"""
    id: int
    company_id: int
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    task_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

