"""
User Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserRoleUpdate
from app.controllers.user_controller import UserController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.utils.permissions import check_company_admin, require_admin
from app.models.user import User

router = APIRouter()


@router.get("/{company_id}/users")
async def get_users(
    company_id: int = Path(..., description="Company ID"),
    search: Optional[str] = Query(None, description="Search in name/email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all users in company
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **search**: Search in name or email
    - **role**: Filter by role
    - **page**: Page number
    - **per_page**: Items per page
    
    Requires: JWT token
    """
    try:
        users = UserController.get_company_users(company_id, current_user, db, search, role)
        
        # Simple pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_users = users[start:end]
        
        total = len(users)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [user.to_dict() for user in paginated_users],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            },
            "message": "Users fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    company_id: int = Path(..., description="Company ID"),
    user_data: UserCreate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new user in company
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token, Admin role in company
    """
    # Check if user is admin in company or super_admin
    if current_user.role != "super_admin" and not check_company_admin(current_user.id, company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for this company"
        )
    
    try:
        user = UserController.create_user(company_id, user_data, current_user, db)
        return success_response(
            data=user.to_dict(),
            message="User created successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/users/{user_id}")
async def get_user(
    company_id: int = Path(..., description="Company ID"),
    user_id: int = Path(..., description="User ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user details
    
    Path Parameters:
    - **company_id**: Company ID
    - **user_id**: User ID
    
    Requires: JWT token
    """
    try:
        user = UserController.get_user(user_id, company_id, current_user, db)
        return success_response(
            data=user.to_dict(include_companies=True),
            message="User details fetched successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/users/{user_id}")
async def update_user(
    company_id: int = Path(..., description="Company ID"),
    user_id: int = Path(..., description="User ID"),
    user_data: UserUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user
    
    Path Parameters:
    - **company_id**: Company ID
    - **user_id**: User ID
    
    Requires: JWT token, Admin role or self
    """
    try:
        user = UserController.update_user(user_id, company_id, user_data, current_user, db)
        return success_response(
            data=user.to_dict(),
            message="User updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/users/{user_id}/role")
async def update_user_role(
    company_id: int = Path(..., description="Company ID"),
    user_id: int = Path(..., description="User ID"),
    role_data: UserRoleUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user role in company
    
    Path Parameters:
    - **company_id**: Company ID
    - **user_id**: User ID
    
    Requires: JWT token, Admin role in company
    """
    # Check if user is admin in company or super_admin
    if current_user.role != "super_admin" and not check_company_admin(current_user.id, company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for this company"
        )
    
    try:
        UserController.update_user_role(user_id, company_id, role_data, current_user, db)
        return success_response(
            data={},
            message="User role updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{company_id}/users/{user_id}")
async def delete_user(
    company_id: int = Path(..., description="Company ID"),
    user_id: int = Path(..., description="User ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete user from company
    
    Path Parameters:
    - **company_id**: Company ID
    - **user_id**: User ID
    
    Requires: JWT token, Admin role in company
    """
    # Check if user is admin in company or super_admin
    if current_user.role != "super_admin" and not check_company_admin(current_user.id, company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for this company"
        )
    
    try:
        UserController.delete_user(user_id, company_id, current_user, db)
        return success_response(
            data={},
            message="User deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

