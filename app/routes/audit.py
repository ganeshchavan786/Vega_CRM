"""
Audit Trail Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.schemas.audit_trail import (
    AuditTrailResponse, AuditTrailListResponse,
    ResourceHistoryResponse, UserActivityResponse
)
from app.services import audit_service
from app.utils.dependencies import get_current_active_user
from app.utils.permissions import require_admin
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("/audit-trails", response_model=AuditTrailListResponse)
async def get_audit_trails(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    action: Optional[str] = Query(None, description="Filter by action: CREATE, UPDATE, DELETE, LOGIN, etc."),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[int] = Query(None, description="Filter by resource ID"),
    status: Optional[str] = Query(None, description="Filter by status: SUCCESS, FAILED"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    search: Optional[str] = Query(None, description="Search in message, email, resource"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit trails with filtering and pagination
    
    Requires: Admin role
    """
    skip = (page - 1) * per_page
    
    audit_trails, total = audit_service.get_audit_trails(
        db=db,
        skip=skip,
        limit=per_page,
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    
    return AuditTrailListResponse(
        audit_trails=[AuditTrailResponse.model_validate(at) for at in audit_trails],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/audit-trails/count")
async def get_audit_trails_count(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get count of audit trails matching filters
    
    Requires: Admin role
    """
    _, total = audit_service.get_audit_trails(
        db=db,
        skip=0,
        limit=1,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        status=status,
        start_date=start_date,
        end_date=end_date
    )
    
    return success_response(
        data={"count": total},
        message="Audit trail count retrieved"
    )


@router.get("/audit-trails/resource/{resource_type}/{resource_id}", response_model=ResourceHistoryResponse)
async def get_resource_history(
    resource_type: str,
    resource_id: int,
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit history for a specific resource
    
    Requires: Admin role
    """
    history = audit_service.get_resource_history(
        db=db,
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit
    )
    
    return ResourceHistoryResponse(
        resource_type=resource_type,
        resource_id=resource_id,
        history=[AuditTrailResponse.model_validate(h) for h in history],
        total=len(history)
    )


@router.get("/audit-trails/user/{user_id}", response_model=UserActivityResponse)
async def get_user_activity(
    user_id: int,
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all audit activities for a specific user
    
    Requires: Admin role
    """
    activities = audit_service.get_user_activity(
        db=db,
        user_id=user_id,
        limit=limit
    )
    
    return UserActivityResponse(
        user_id=user_id,
        activities=[AuditTrailResponse.model_validate(a) for a in activities],
        total=len(activities)
    )


@router.get("/audit-trails/actions")
async def get_available_actions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of available action types for filtering
    
    Requires: Admin role
    """
    actions = [
        "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT",
        "IMPORT", "EXPORT", "CONVERT", "ASSIGN", "BULK_UPDATE"
    ]
    
    return success_response(
        data={"actions": actions},
        message="Available actions retrieved"
    )


@router.get("/audit-trails/resource-types")
async def get_available_resource_types(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of available resource types for filtering
    
    Requires: Admin role
    """
    resource_types = [
        "User", "Company", "Customer", "Contact", "Lead",
        "Deal", "Task", "Activity", "Permission", "EmailSequence"
    ]
    
    return success_response(
        data={"resource_types": resource_types},
        message="Available resource types retrieved"
    )
