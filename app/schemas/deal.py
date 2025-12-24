"""
Deal Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class DealBase(BaseModel):
    """Base deal schema"""
    deal_name: str = Field(..., min_length=2, max_length=255)
    deal_value: Decimal = Field(..., ge=0)
    currency: Optional[str] = Field("USD", max_length=10)
    stage: Optional[str] = Field("prospect", pattern="^(prospect|qualified|proposal|negotiation|closed_won|closed_lost)$")
    probability: Optional[int] = Field(0, ge=0, le=100)
    expected_close_date: Optional[date] = None
    notes: Optional[str] = None


class DealCreate(DealBase):
    """Create deal schema"""
    customer_id: int
    lead_id: Optional[int] = None
    status: Optional[str] = Field("open", pattern="^(open|won|lost)$")
    assigned_to: Optional[int] = None


class DealUpdate(BaseModel):
    """Update deal schema - all fields optional"""
    deal_name: Optional[str] = Field(None, min_length=2, max_length=255)
    deal_value: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    stage: Optional[str] = Field(None, pattern="^(prospect|qualified|proposal|negotiation|closed_won|closed_lost)$")
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    actual_close_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(open|won|lost)$")
    loss_reason: Optional[str] = None
    notes: Optional[str] = None
    assigned_to: Optional[int] = None


class DealResponse(DealBase):
    """Deal response schema"""
    id: int
    company_id: int
    customer_id: int
    lead_id: Optional[int] = None
    status: str
    actual_close_date: Optional[date] = None
    loss_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

