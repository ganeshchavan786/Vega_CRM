"""
Permission Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.permission import (
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RolePermissionCreate, RolePermissionUpdate, RolePermissionResponse,
    BulkRolePermissionUpdate, PermissionListResponse, RolePermissionListResponse,
    CheckPermissionRequest, CheckPermissionResponse
)
from app.controllers.permission_controller import PermissionController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.utils.permissions import require_admin, has_permission
from app.models.user import User

router = APIRouter()


# Permission CRUD
@router.get("/permissions", response_model=PermissionListResponse)
async def get_permissions(
    resource: Optional[str] = Query(None, description="Filter by resource"),
    action: Optional[str] = Query(None, description="Filter by action"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all permissions
    
    Query Parameters:
    - **resource**: Filter by resource name
    - **action**: Filter by action name
    
    Requires: Admin role
    """
    try:
        permissions = PermissionController.get_permissions(db, resource, action)
        return PermissionListResponse(
            permissions=[PermissionResponse.model_validate(p) for p in permissions],
            total=len(permissions)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: int = Path(..., description="Permission ID"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get permission by ID
    
    Path Parameters:
    - **permission_id**: Permission ID
    
    Requires: Admin role
    """
    try:
        permission = PermissionController.get_permission(permission_id, db)
        return PermissionResponse.model_validate(permission)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/permissions", status_code=status.HTTP_201_CREATED, response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create new permission
    
    Requires: Admin role
    """
    try:
        permission = PermissionController.create_permission(permission_data, db)
        return PermissionResponse.model_validate(permission)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int = Path(..., description="Permission ID"),
    permission_data: PermissionUpdate = ...,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update permission
    
    Path Parameters:
    - **permission_id**: Permission ID
    
    Requires: Admin role
    """
    try:
        permission = PermissionController.update_permission(permission_id, permission_data, db)
        return PermissionResponse.model_validate(permission)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: int = Path(..., description="Permission ID"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete permission
    
    Path Parameters:
    - **permission_id**: Permission ID
    
    Requires: Admin role
    """
    try:
        PermissionController.delete_permission(permission_id, db)
        return success_response(
            data={},
            message="Permission deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Role Permission CRUD
@router.get("/role-permissions", response_model=RolePermissionListResponse)
async def get_role_permissions(
    role: Optional[str] = Query(None, description="Filter by role"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    permission_id: Optional[int] = Query(None, description="Filter by permission ID"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all role permissions
    
    Query Parameters:
    - **role**: Filter by role
    - **company_id**: Filter by company ID
    - **permission_id**: Filter by permission ID
    
    Requires: Admin role
    """
    try:
        role_permissions = PermissionController.get_role_permissions(db, role, company_id, permission_id)
        return RolePermissionListResponse(
            role_permissions=[RolePermissionResponse.model_validate(rp) for rp in role_permissions],
            total=len(role_permissions)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/role-permissions", status_code=status.HTTP_201_CREATED, response_model=RolePermissionResponse)
async def create_role_permission(
    role_permission_data: RolePermissionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create role permission
    
    Requires: Admin role
    """
    try:
        role_permission = PermissionController.create_role_permission(role_permission_data, db)
        return RolePermissionResponse.model_validate(role_permission)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/role-permissions/{role_permission_id}", response_model=RolePermissionResponse)
async def update_role_permission(
    role_permission_id: int = Path(..., description="Role Permission ID"),
    role_permission_data: RolePermissionUpdate = ...,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update role permission
    
    Path Parameters:
    - **role_permission_id**: Role Permission ID
    
    Requires: Admin role
    """
    try:
        role_permission = PermissionController.update_role_permission(
            role_permission_id, role_permission_data, db
        )
        return RolePermissionResponse.model_validate(role_permission)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/role-permissions/bulk-update")
async def bulk_update_role_permissions(
    bulk_data: BulkRolePermissionUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Bulk update role permissions
    
    Requires: Admin role
    """
    try:
        updated_permissions = PermissionController.bulk_update_role_permissions(bulk_data, db)
        return success_response(
            data=[RolePermissionResponse.model_validate(rp).model_dump() for rp in updated_permissions],
            message=f"Updated {len(updated_permissions)} role permissions"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/role-permissions/{role_permission_id}")
async def delete_role_permission(
    role_permission_id: int = Path(..., description="Role Permission ID"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete role permission
    
    Path Parameters:
    - **role_permission_id**: Role Permission ID
    
    Requires: Admin role
    """
    try:
        PermissionController.delete_role_permission(role_permission_id, db)
        return success_response(
            data={},
            message="Role permission deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Permission checking
@router.post("/check-permission", response_model=CheckPermissionResponse)
async def check_permission(
    check_data: CheckPermissionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user has a specific permission
    
    Requires: Authenticated user
    """
    try:
        # Use existing has_permission function
        has_perm = has_permission(
            current_user,
            check_data.resource,
            check_data.action,
            check_data.company_id,
            db
        )
        
        # Get permission details if exists
        permission = None
        try:
            perm = db.query(Permission).filter(
                Permission.resource == check_data.resource,
                Permission.action == check_data.action
            ).first()
            if perm:
                permission = PermissionResponse.model_validate(perm)
        except:
            pass
        
        return CheckPermissionResponse(
            has_permission=has_perm,
            permission=permission
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Copy global permissions to company
@router.post("/permissions/copy-to-company/{company_id}")
async def copy_permissions_to_company(
    company_id: int = Path(..., description="Target company ID"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Copy all global role permissions to a specific company
    
    Path Parameters:
    - **company_id**: Target company ID
    
    Requires: Admin role
    """
    try:
        copied_count = PermissionController.copy_global_to_company(company_id, db)
        return success_response(
            data={"copied_count": copied_count},
            message=f"Successfully copied {copied_count} permissions to company {company_id}"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

