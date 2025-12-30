"""
Permission Schemas
Pydantic models for permission-related requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Permission Schemas
class PermissionBase(BaseModel):
    """Base permission schema"""
    resource: str = Field(..., description="Resource name (e.g., 'customer', 'lead', 'deal')")
    action: str = Field(..., description="Action name (e.g., 'create', 'read', 'update', 'delete')")
    description: Optional[str] = Field(None, description="Permission description")


class PermissionCreate(PermissionBase):
    """Schema for creating a permission"""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating a permission"""
    resource: Optional[str] = Field(None, description="Resource name")
    action: Optional[str] = Field(None, description="Action name")
    description: Optional[str] = Field(None, description="Permission description")


class PermissionResponse(PermissionBase):
    """Schema for permission response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Role Permission Schemas
class RolePermissionBase(BaseModel):
    """Base role permission schema"""
    permission_id: int = Field(..., description="Permission ID")
    role: str = Field(..., description="Role name (super_admin, admin, manager, sales_rep, user)")
    company_id: Optional[int] = Field(None, description="Company ID (None for global role)")
    granted: bool = Field(True, description="Whether permission is granted")


class RolePermissionCreate(RolePermissionBase):
    """Schema for creating a role permission"""
    pass


class RolePermissionUpdate(BaseModel):
    """Schema for updating a role permission"""
    granted: Optional[bool] = Field(None, description="Whether permission is granted")


class RolePermissionResponse(RolePermissionBase):
    """Schema for role permission response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RolePermissionWithPermission(RolePermissionResponse):
    """Role permission response with permission details"""
    permission: PermissionResponse


# Bulk Permission Schemas
class BulkRolePermissionUpdate(BaseModel):
    """Schema for bulk updating role permissions"""
    role: str = Field(..., description="Role name")
    company_id: Optional[int] = Field(None, description="Company ID (None for global role)")
    permission_updates: List[dict] = Field(..., description="List of {permission_id, granted} objects")


class PermissionListResponse(BaseModel):
    """Schema for permission list response"""
    permissions: List[PermissionResponse]
    total: int


class RolePermissionListResponse(BaseModel):
    """Schema for role permission list response"""
    role_permissions: List[RolePermissionResponse]
    total: int


class CheckPermissionRequest(BaseModel):
    """Schema for checking permission"""
    resource: str = Field(..., description="Resource name")
    action: str = Field(..., description="Action name")
    company_id: Optional[int] = Field(None, description="Company ID")


class CheckPermissionResponse(BaseModel):
    """Schema for permission check response"""
    has_permission: bool
    permission: Optional[PermissionResponse] = None
    role_permission: Optional[RolePermissionResponse] = None

