"""
Email Sequence Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class EmailTemplate(BaseModel):
    """Email template in sequence"""
    email_number: int = Field(..., ge=1, description="Email number in sequence (1, 2, 3...)")
    delay_days: int = Field(..., ge=0, description="Days after sequence start")
    subject: str = Field(..., description="Email subject (supports {first_name}, {company_name})")
    body: str = Field(..., description="Email body (supports {first_name}, {company_name})")


class EmailSequenceBase(BaseModel):
    """Base email sequence schema"""
    name: str = Field(..., description="Sequence name")
    description: Optional[str] = None
    is_active: bool = Field(True, description="Is sequence active")
    trigger_on_creation: bool = Field(True, description="Trigger on lead creation")
    trigger_score_threshold: Optional[int] = Field(None, ge=0, le=100, description="Trigger when score reaches threshold")
    total_emails: int = Field(5, ge=1, le=20, description="Number of emails in sequence")
    sequence_duration_days: int = Field(14, ge=1, description="Total duration in days")
    email_templates: Optional[List[Dict]] = None


class EmailSequenceCreate(EmailSequenceBase):
    """Create email sequence"""
    pass


class EmailSequenceUpdate(BaseModel):
    """Update email sequence"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    trigger_on_creation: Optional[bool] = None
    trigger_score_threshold: Optional[int] = Field(None, ge=0, le=100)
    total_emails: Optional[int] = Field(None, ge=1, le=20)
    sequence_duration_days: Optional[int] = Field(None, ge=1)
    email_templates: Optional[List[Dict]] = None


class EmailSequenceResponse(EmailSequenceBase):
    """Email sequence response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmailSequenceStatus(BaseModel):
    """Email sequence status for lead"""
    sequence_started: bool
    sequence_id: Optional[int] = None
    total_emails: int
    sent: int
    opened: int
    clicked: int
    pending: int
    emails: Optional[List[Dict]] = None

