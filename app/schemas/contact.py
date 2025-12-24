"""
Contact Schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class ContactBase(BaseModel):
    """Base contact schema"""
    name: str = Field(..., min_length=2, max_length=200)
    job_title: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, pattern="^(decision_maker|influencer|user|gatekeeper|champion|economic_buyer)$")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    preferred_channel: Optional[str] = Field(None, pattern="^(email|whatsapp|phone|sms|linkedin)$")
    influence_score: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    is_primary_contact: Optional[bool] = False


class ContactCreate(ContactBase):
    """Create contact schema"""
    account_id: int = Field(..., description="Account (Customer) ID")


class ContactUpdate(BaseModel):
    """Update contact schema - all fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    job_title: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, pattern="^(decision_maker|influencer|user|gatekeeper|champion|economic_buyer)$")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    preferred_channel: Optional[str] = Field(None, pattern="^(email|whatsapp|phone|sms|linkedin)$")
    influence_score: Optional[str] = Field(None, pattern="^(high|medium|low)$")
    is_primary_contact: Optional[bool] = None
    account_id: Optional[int] = None


class ContactResponse(ContactBase):
    """Contact response schema"""
    id: int
    company_id: int
    account_id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

