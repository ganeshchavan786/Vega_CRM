"""
Task Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    task_type: Optional[str] = Field("general", pattern="^(call|email|meeting|general|follow_up)$")
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high|urgent)$")
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Create task schema"""
    status: Optional[str] = Field("pending", pattern="^(pending|in_progress|completed|cancelled)$")
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    assigned_to: int


class TaskUpdate(BaseModel):
    """Update task schema - all fields optional"""
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    task_type: Optional[str] = Field(None, pattern="^(call|email|meeting|general|follow_up)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_to: Optional[int] = None


class TaskResponse(TaskBase):
    """Task response schema"""
    id: int
    company_id: int
    status: str
    completed_at: Optional[datetime] = None
    customer_id: Optional[int] = None
    lead_id: Optional[int] = None
    deal_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

