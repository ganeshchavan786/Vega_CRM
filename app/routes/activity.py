"""
Activity Logging Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.activity import ActivityCreate, ActivityUpdate
from app.controllers.activity_controller import ActivityController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("/{company_id}/activities")
async def get_activities(
    company_id: int = Path(..., description="Company ID"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    lead_id: Optional[int] = Query(None, description="Filter by lead"),
    deal_id: Optional[int] = Query(None, description="Filter by deal"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all activities in company"""
    try:
        activities = ActivityController.get_activities(
            company_id, current_user, db, activity_type, customer_id, lead_id, deal_id, user_id
        )
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_activities = activities[start:end]
        
        total = len(activities)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [activity.to_dict(include_relations=True) for activity in paginated_activities],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            },
            "message": "Activities fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/activities", status_code=status.HTTP_201_CREATED)
async def create_activity(
    company_id: int = Path(..., description="Company ID"),
    activity_data: ActivityCreate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Log new activity"""
    try:
        activity = ActivityController.create_activity(company_id, activity_data, current_user, db)
        return success_response(
            data=activity.to_dict(include_relations=True),
            message="Activity logged successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/activities/timeline")
async def get_timeline(
    company_id: int = Path(..., description="Company ID"),
    customer_id: Optional[int] = Query(None, description="Customer ID"),
    lead_id: Optional[int] = Query(None, description="Lead ID"),
    deal_id: Optional[int] = Query(None, description="Deal ID"),
    limit: int = Query(50, ge=1, le=200, description="Number of activities"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get activity timeline"""
    try:
        # Ensure limit is within valid range
        limit = max(1, min(200, limit or 50))
        activities = ActivityController.get_timeline(
            company_id, current_user, db, customer_id, lead_id, deal_id, limit
        )
        return success_response(
            data=[activity.to_dict(include_relations=True) for activity in activities],
            message="Activity timeline fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/activities/{activity_id}")
async def get_activity(
    company_id: int = Path(..., description="Company ID"),
    activity_id: int = Path(..., description="Activity ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get activity details"""
    try:
        activity = ActivityController.get_activity(activity_id, company_id, current_user, db)
        return success_response(
            data=activity.to_dict(include_relations=True),
            message="Activity details fetched successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/activities/{activity_id}")
async def update_activity(
    company_id: int = Path(..., description="Company ID"),
    activity_id: int = Path(..., description="Activity ID"),
    activity_data: ActivityUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update activity"""
    try:
        activity = ActivityController.update_activity(
            activity_id, company_id, activity_data, current_user, db
        )
        return success_response(
            data=activity.to_dict(include_relations=True),
            message="Activity updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{company_id}/activities/{activity_id}")
async def delete_activity(
    company_id: int = Path(..., description="Company ID"),
    activity_id: int = Path(..., description="Activity ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete activity"""
    try:
        ActivityController.delete_activity(activity_id, company_id, current_user, db)
        return success_response(
            data={},
            message="Activity deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

