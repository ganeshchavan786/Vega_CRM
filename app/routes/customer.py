"""
Customer Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.controllers.customer_controller import CustomerController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("/{company_id}/customers")
async def get_customers(
    company_id: int = Path(..., description="Company ID"),
    search: Optional[str] = Query(None, description="Search in name/email/phone"),
    status: Optional[str] = Query(None, description="Filter by status"),
    customer_type: Optional[str] = Query(None, description="Filter by type"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all customers in company
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **search**: Search in name, email, or phone
    - **status**: Filter by status (active/inactive/prospect/lost)
    - **customer_type**: Filter by type (individual/business)
    - **assigned_to**: Filter by assigned user ID
    - **page**: Page number
    - **per_page**: Items per page
    
    Requires: JWT token
    """
    try:
        customers = CustomerController.get_customers(
            company_id, current_user, db, search, status, customer_type, assigned_to
        )
        
        # Simple pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_customers = customers[start:end]
        
        total = len(customers)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [customer.to_dict(include_relations=True) for customer in paginated_customers],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            },
            "message": "Customers fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/customers", status_code=status.HTTP_201_CREATED)
async def create_customer(
    company_id: int = Path(..., description="Company ID"),
    customer_data: CustomerCreate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new customer
    
    Path Parameters:
    - **company_id**: Company ID
    
    Required fields:
    - **name**: Customer name
    
    Requires: JWT token
    """
    try:
        customer = CustomerController.create_customer(company_id, customer_data, current_user, db)
        return success_response(
            data=customer.to_dict(include_relations=True),
            message="Customer created successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/customers/{customer_id}")
async def get_customer(
    company_id: int = Path(..., description="Company ID"),
    customer_id: int = Path(..., description="Customer ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get customer details
    
    Path Parameters:
    - **company_id**: Company ID
    - **customer_id**: Customer ID
    
    Requires: JWT token
    """
    try:
        customer = CustomerController.get_customer(customer_id, company_id, current_user, db)
        return success_response(
            data=customer.to_dict(include_relations=True),
            message="Customer details fetched successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/customers/{customer_id}")
async def update_customer(
    company_id: int = Path(..., description="Company ID"),
    customer_id: int = Path(..., description="Customer ID"),
    customer_data: CustomerUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update customer
    
    Path Parameters:
    - **company_id**: Company ID
    - **customer_id**: Customer ID
    
    Requires: JWT token
    """
    try:
        customer = CustomerController.update_customer(
            customer_id, company_id, customer_data, current_user, db
        )
        return success_response(
            data=customer.to_dict(include_relations=True),
            message="Customer updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{company_id}/customers/{customer_id}")
async def delete_customer(
    company_id: int = Path(..., description="Company ID"),
    customer_id: int = Path(..., description="Customer ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete customer
    
    Path Parameters:
    - **company_id**: Company ID
    - **customer_id**: Customer ID
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        CustomerController.delete_customer(customer_id, company_id, current_user, db)
        return success_response(
            data={},
            message="Customer deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/customers/{customer_id}/recalculate-health-score")
async def recalculate_health_score(
    company_id: int = Path(..., description="Company ID"),
    customer_id: int = Path(..., description="Customer ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Recalculate health score for a customer
    
    Path Parameters:
    - **company_id**: Company ID
    - **customer_id**: Customer ID
    
    Requires: JWT token
    """
    try:
        from app.utils.health_score import HealthScoreCalculator
        
        new_score = HealthScoreCalculator.update_health_score(
            customer_id, company_id, db, force_update=True
        )
        
        if new_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return success_response(
            data={"health_score": new_score},
            message="Health score recalculated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalculating health score: {str(e)}"
        )


@router.post("/{company_id}/customers/{customer_id}/recalculate-lifecycle-stage")
async def recalculate_lifecycle_stage(
    company_id: int = Path(..., description="Company ID"),
    customer_id: int = Path(..., description="Customer ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Recalculate lifecycle stage for a customer
    
    Path Parameters:
    - **company_id**: Company ID
    - **customer_id**: Customer ID
    
    Requires: JWT token
    """
    try:
        from app.utils.lifecycle_stage import LifecycleStageAutomation
        
        new_stage = LifecycleStageAutomation.update_lifecycle_stage(
            customer_id, company_id, db, force_update=True
        )
        
        if new_stage is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return success_response(
            data={"lifecycle_stage": new_stage},
            message="Lifecycle stage recalculated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalculating lifecycle stage: {str(e)}"
        )


@router.post("/{company_id}/customers/batch-recalculate-lifecycle-stages")
async def batch_recalculate_lifecycle_stages(
    company_id: int = Path(..., description="Company ID"),
    customer_ids: Optional[List[int]] = Query(None, description="List of customer IDs (optional, all if not provided)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Batch recalculate lifecycle stages for multiple customers
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **customer_ids**: Optional list of customer IDs (all customers if not provided)
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        from app.utils.lifecycle_stage import LifecycleStageAutomation
        from app.models.user_company import UserCompany
        
        # Check if user has permission (admin/manager)
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id,
            UserCompany.role.in_(["admin", "manager"])
        ).first()
        
        if not user_company and current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        result = LifecycleStageAutomation.batch_update_lifecycle_stages(
            company_id, db, customer_ids
        )
        
        return success_response(
            data=result,
            message=f"Lifecycle stages recalculated: {result['updated']} updated, {result['unchanged']} unchanged"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalculating lifecycle stages: {str(e)}"
        )


@router.post("/{company_id}/customers/batch-recalculate-health-scores")
async def batch_recalculate_health_scores(
    company_id: int = Path(..., description="Company ID"),
    customer_ids: Optional[List[int]] = Query(None, description="List of customer IDs (optional, all if not provided)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Batch recalculate health scores for multiple customers
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **customer_ids**: Optional list of customer IDs (all customers if not provided)
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        from app.utils.health_score import HealthScoreCalculator
        
        # Check if user has permission (admin/manager)
        from app.models.user_company import UserCompany
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id,
            UserCompany.role.in_(["admin", "manager"])
        ).first()
        
        if not user_company and current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        result = HealthScoreCalculator.batch_update_health_scores(
            company_id, db, customer_ids
        )
        
        return success_response(
            data=result,
            message=f"Health scores recalculated: {result['updated']} updated, {result['unchanged']} unchanged"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalculating health scores: {str(e)}"
        )


@router.get("/{company_id}/customers-stats")
async def get_customer_stats(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get customer statistics for company
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        stats = CustomerController.get_customer_stats(company_id, db)
        return success_response(
            data=stats,
            message="Customer statistics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

