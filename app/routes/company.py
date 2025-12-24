"""
Company Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.controllers.company_controller import CompanyController
from app.utils.dependencies import get_current_active_user, require_role
from app.utils.helpers import success_response, paginate
from app.models.user import User

router = APIRouter()


@router.get("")
async def get_companies(
    search: Optional[str] = Query(None, description="Search in company name/email"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all companies accessible to current user
    
    Query Parameters:
    - **search**: Search in company name or email
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 10, max: 100)
    
    Requires: JWT token
    """
    try:
        companies = CompanyController.get_user_companies(current_user, db, search)
        
        # Simple pagination (manual)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_companies = companies[start:end]
        
        total = len(companies)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [company.to_dict() for company in paginated_companies],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            },
            "message": "Companies fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new company
    
    Required fields:
    - **name**: Company name
    - **email**: Company email (unique)
    
    Requires: JWT token
    """
    try:
        company = CompanyController.create_company(company_data, current_user, db)
        return success_response(
            data=company.to_dict(),
            message="Company created successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}")
async def get_company(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get company details by ID
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token, Access to company
    """
    try:
        company = CompanyController.get_company(company_id, current_user, db)
        return success_response(
            data=company.to_dict(),
            message="Company details fetched successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}")
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update company
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token, Admin role in company
    """
    try:
        company = CompanyController.update_company(company_id, company_data, current_user, db)
        return success_response(
            data=company.to_dict(),
            message="Company updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    """
    Delete company
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token, Super Admin role
    """
    try:
        CompanyController.delete_company(company_id, current_user, db)
        return success_response(
            data={},
            message="Company deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/select/{company_id}")
async def select_company(
    company_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Select company (set as active company for session)
    
    Path Parameters:
    - **company_id**: Company ID to select
    
    Returns new JWT token with company context
    
    Requires: JWT token, Access to company
    """
    try:
        from app.utils.security import create_access_token
        
        # Verify access to company
        company = CompanyController.get_company(company_id, current_user, db)
        
        # Create new token with company context
        token_data = {
            "user_id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "company_id": company_id
        }
        new_token = create_access_token(token_data)
        
        return success_response(
            data={
                "company_id": company.id,
                "company_name": company.name,
                "user_role": current_user.role,
                "new_token": new_token
            },
            message="Company selected successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

