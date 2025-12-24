"""
Lead Schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class LeadBase(BaseModel):
    """Base lead schema"""
    lead_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    source: Optional[str] = None
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high)$")
    estimated_value: Optional[Decimal] = None
    notes: Optional[str] = None
    industry: Optional[str] = None


class LeadCreate(LeadBase):
    """Create lead schema - includes all enterprise fields"""
    # Personal Information
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    
    # Source Attribution
    campaign: Optional[str] = Field(None, max_length=200)
    medium: Optional[str] = Field(None, max_length=50)
    term: Optional[str] = Field(None, max_length=200)
    
    # Lead Management
    status: Optional[str] = Field("new", pattern="^(new|contacted|qualified|converted|lost)$")
    stage: Optional[str] = Field(None, max_length=50)
    
    # Qualification Fields
    interest_product: Optional[str] = Field(None, max_length=200)
    budget_range: Optional[str] = Field(None, max_length=100)
    authority_level: Optional[str] = Field(None, max_length=50)
    timeline: Optional[str] = Field(None, max_length=100)
    
    # Foreign Keys
    customer_id: Optional[int] = None
    assigned_to: Optional[int] = None


class LeadUpdate(BaseModel):
    """Update lead schema - all fields optional"""
    lead_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(new|contacted|qualified|converted|lost)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    estimated_value: Optional[Decimal] = None
    notes: Optional[str] = None
    industry: Optional[str] = None
    
    # Personal Information
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    
    # Source Attribution
    campaign: Optional[str] = Field(None, max_length=200)
    medium: Optional[str] = Field(None, max_length=50)
    term: Optional[str] = Field(None, max_length=200)
    
    # Lead Management
    stage: Optional[str] = Field(None, max_length=50)
    
    # Qualification Fields
    interest_product: Optional[str] = Field(None, max_length=200)
    budget_range: Optional[str] = Field(None, max_length=100)
    authority_level: Optional[str] = Field(None, max_length=50)
    timeline: Optional[str] = Field(None, max_length=100)
    
    # Foreign Keys
    customer_id: Optional[int] = None
    assigned_to: Optional[int] = None


class LeadResponse(LeadBase):
    """Lead response schema"""
    id: int
    company_id: int
    customer_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

