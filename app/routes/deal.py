"""
Deal Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.deal import DealCreate, DealUpdate
from app.controllers.deal_controller import DealController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("/{company_id}/deals")
async def get_deals(
    company_id: int = Path(..., description="Company ID"),
    search: Optional[str] = Query(None, description="Search in deal name"),
    stage: Optional[str] = Query(None, description="Filter by stage"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all deals in company"""
    try:
        deals = DealController.get_deals(
            company_id, current_user, db, search, stage, status, assigned_to
        )
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_deals = deals[start:end]
        
        total = len(deals)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [deal.to_dict(include_relations=True) for deal in paginated_deals],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            },
            "message": "Deals fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/deals", status_code=status.HTTP_201_CREATED)
async def create_deal(
    company_id: int = Path(..., description="Company ID"),
    deal_data: DealCreate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new deal"""
    try:
        deal = DealController.create_deal(company_id, deal_data, current_user, db)
        return success_response(
            data=deal.to_dict(include_relations=True),
            message="Deal created successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/deals/{deal_id}")
async def get_deal(
    company_id: int = Path(..., description="Company ID"),
    deal_id: int = Path(..., description="Deal ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get deal details"""
    try:
        deal = DealController.get_deal(deal_id, company_id, current_user, db)
        return success_response(
            data=deal.to_dict(include_relations=True),
            message="Deal details fetched successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/deals/{deal_id}")
async def update_deal(
    company_id: int = Path(..., description="Company ID"),
    deal_id: int = Path(..., description="Deal ID"),
    deal_data: DealUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update deal"""
    try:
        deal = DealController.update_deal(deal_id, company_id, deal_data, current_user, db)
        return success_response(
            data=deal.to_dict(include_relations=True),
            message="Deal updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{company_id}/deals/{deal_id}")
async def delete_deal(
    company_id: int = Path(..., description="Company ID"),
    deal_id: int = Path(..., description="Deal ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete deal"""
    try:
        DealController.delete_deal(deal_id, company_id, current_user, db)
        return success_response(
            data={},
            message="Deal deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/deals-stats")
async def get_deal_stats(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get deal statistics and pipeline"""
    try:
        stats = DealController.get_deal_stats(company_id, db)
        return success_response(
            data=stats,
            message="Deal statistics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

