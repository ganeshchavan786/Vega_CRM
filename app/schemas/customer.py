"""
Customer Schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CustomerBase(BaseModel):
    """Base customer schema"""
    name: str = Field(..., min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    customer_type: Optional[str] = Field("individual", pattern="^(individual|business)$")
    industry: Optional[str] = None
    company_name: Optional[str] = None
    website: Optional[str] = None


class CustomerCreate(CustomerBase):
    """Create customer schema"""
    status: Optional[str] = Field("active", pattern="^(active|inactive|prospect|lost)$")
    source: Optional[str] = None
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high)$")
    notes: Optional[str] = None
    assigned_to: Optional[int] = None
    # Enterprise fields
    account_type: Optional[str] = Field(None, pattern="^(customer|prospect|partner|competitor|reseller)$")
    company_size: Optional[str] = None
    annual_revenue: Optional[Decimal] = None
    gstin: Optional[str] = Field(None, max_length=15)
    health_score: Optional[str] = Field(None, pattern="^(green|yellow|red|black)$")
    lifecycle_stage: Optional[str] = Field(None, pattern="^(MQA|SQA|Customer|Churned)$")
    is_active: Optional[bool] = True
    account_owner_id: Optional[int] = None


class CustomerUpdate(BaseModel):
    """Update customer schema - all fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    customer_type: Optional[str] = Field(None, pattern="^(individual|business)$")
    industry: Optional[str] = None
    company_name: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|prospect|lost)$")
    source: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    credit_limit: Optional[Decimal] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    assigned_to: Optional[int] = None
    # Enterprise fields
    account_type: Optional[str] = Field(None, pattern="^(customer|prospect|partner|competitor|reseller)$")
    company_size: Optional[str] = None
    annual_revenue: Optional[Decimal] = None
    gstin: Optional[str] = Field(None, max_length=15)
    health_score: Optional[str] = Field(None, pattern="^(green|yellow|red|black)$")
    lifecycle_stage: Optional[str] = Field(None, pattern="^(MQA|SQA|Customer|Churned)$")
    is_active: Optional[bool] = None
    account_owner_id: Optional[int] = None


class CustomerResponse(CustomerBase):
    """Customer response schema"""
    id: int
    company_id: int
    customer_code: Optional[str] = None
    status: str
    source: Optional[str] = None
    priority: str
    credit_limit: Decimal
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    # Enterprise fields
    account_type: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[Decimal] = None
    gstin: Optional[str] = None
    health_score: Optional[str] = None
    lifecycle_stage: Optional[str] = None
    is_active: Optional[bool] = True
    account_owner_id: Optional[int] = None
    
    class Config:
        from_attributes = True

