"""
Report Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ReportBase(BaseModel):
    """Base report schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    report_type: str = Field(..., description="Report type: sales, leads, activities, custom")
    config: Optional[Dict[str, Any]] = Field(None, description="Report configuration")


class ReportCreate(ReportBase):
    """Report creation schema"""
    company_id: Optional[int] = Field(None, description="Company ID (null for global)")
    is_public: bool = Field(False, description="Available to all users in company")
    allowed_roles: Optional[List[str]] = Field(None, description="Roles that can access")
    is_scheduled: bool = Field(False, description="Enable scheduling")
    schedule_cron: Optional[str] = Field(None, description="Cron expression for scheduling")


class ReportUpdate(BaseModel):
    """Report update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    allowed_roles: Optional[List[str]] = None
    is_scheduled: Optional[bool] = None
    schedule_cron: Optional[str] = None


class ReportResponse(BaseModel):
    """Report response schema"""
    id: int
    name: str
    description: Optional[str] = None
    report_type: str
    config: Optional[Dict[str, Any]] = None
    company_id: Optional[int] = None
    created_by: int
    is_public: bool
    allowed_roles: Optional[List[str]] = None
    is_scheduled: bool
    schedule_cron: Optional[str] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Report list response"""
    reports: List[ReportResponse]
    total: int


class ReportRunRequest(BaseModel):
    """Report run request schema"""
    filters: Optional[Dict[str, Any]] = Field(None, description="Runtime filters")
    format: str = Field("json", description="Output format: json, csv, pdf")


class ReportRunResponse(BaseModel):
    """Report run response schema"""
    report_id: int
    report_name: str
    executed_at: datetime
    row_count: int
    data: Optional[List[Dict[str, Any]]] = None
    download_url: Optional[str] = None


class ReportTypeInfo(BaseModel):
    """Report type info"""
    type: str
    name: str
    description: str
    available_filters: List[str]


class ReportTypesResponse(BaseModel):
    """Report types list response"""
    types: List[ReportTypeInfo]
