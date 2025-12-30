"""
System Log Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.schemas.log import (
    LogResponse, LogListResponse,
    LogStatisticsResponse, LogCleanupResponse
)
from app.services import log_service
from app.utils.dependencies import get_current_active_user
from app.utils.permissions import require_admin, require_super_admin
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("/logs", response_model=LogListResponse)
async def get_logs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    level: Optional[str] = Query(None, description="Filter by level: INFO, WARNING, ERROR, DEBUG"),
    category: Optional[str] = Query(None, description="Filter by category: Auth, Email, Admin, System, Security"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    search: Optional[str] = Query(None, description="Search in message, action, email"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get system logs with filtering and pagination
    
    Requires: Admin role
    """
    skip = (page - 1) * per_page
    
    logs = log_service.get_logs(
        db=db,
        skip=skip,
        limit=per_page,
        level=level,
        category=category,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    
    total = log_service.get_logs_count(
        db=db,
        level=level,
        category=category,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    
    return LogListResponse(
        logs=[LogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/logs/count")
async def get_logs_count(
    level: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get count of logs matching filters
    
    Requires: Admin role
    """
    total = log_service.get_logs_count(
        db=db,
        level=level,
        category=category,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return success_response(
        data={"count": total},
        message="Log count retrieved"
    )


@router.get("/logs/statistics", response_model=LogStatisticsResponse)
async def get_log_statistics(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get log statistics for dashboard
    
    Requires: Admin role
    """
    stats = log_service.get_log_statistics(db=db, days=days)
    return LogStatisticsResponse(**stats)


@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = Query(50, ge=1, le=200, description="Number of recent logs"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get most recent logs
    
    Requires: Admin role
    """
    logs = log_service.get_recent_logs(db=db, limit=limit)
    
    return success_response(
        data={
            "logs": [LogResponse.model_validate(log).model_dump() for log in logs],
            "count": len(logs)
        },
        message="Recent logs retrieved"
    )


@router.delete("/logs/cleanup", response_model=LogCleanupResponse)
async def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365, description="Delete logs older than this many days"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Delete logs older than specified days
    
    Requires: Super Admin role
    """
    deleted_count = log_service.cleanup_old_logs(db=db, days=days)
    
    return LogCleanupResponse(
        deleted_count=deleted_count,
        message=f"Deleted {deleted_count} logs older than {days} days"
    )


@router.get("/logs/levels")
async def get_available_levels(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of available log levels
    
    Requires: Admin role
    """
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    
    return success_response(
        data={"levels": levels},
        message="Available log levels retrieved"
    )


@router.get("/logs/categories")
async def get_available_categories(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of available log categories
    
    Requires: Admin role
    """
    categories = ["Auth", "User Activity", "Email", "Admin", "System", "Security"]
    
    return success_response(
        data={"categories": categories},
        message="Available log categories retrieved"
    )
