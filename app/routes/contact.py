"""
Contact Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.controllers.contact_controller import ContactController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("/{company_id}/contacts", response_model=dict)
async def get_contacts(
    company_id: int = Path(..., description="Company ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    search: Optional[str] = Query(None, description="Search in name/email/phone/job_title"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all contacts in company
    """
    try:
        contacts = ContactController.get_contacts(
            company_id=company_id,
            account_id=account_id,
            current_user=current_user,
            db=db,
            search=search
        )
        
        # Pagination
        total = len(contacts)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_contacts = contacts[start:end]
        
        return {
            "success": True,
            "data": [contact.to_dict(include_relations=True) for contact in paginated_contacts],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if total > 0 else 1
            },
            "message": f"Retrieved {len(paginated_contacts)} contacts"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving contacts: {str(e)}"
        )


@router.post("/{company_id}/contacts", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_contact(
    company_id: int = Path(..., description="Company ID"),
    contact_data: ContactCreate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new contact
    """
    try:
        contact = ContactController.create_contact(
            company_id=company_id,
            contact_data=contact_data,
            current_user=current_user,
            db=db
        )
        
        return success_response(
            data=contact.to_dict(include_relations=True),
            message="Contact created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating contact: {str(e)}"
        )


@router.get("/{company_id}/contacts/{contact_id}", response_model=dict)
async def get_contact(
    company_id: int = Path(..., description="Company ID"),
    contact_id: int = Path(..., description="Contact ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get contact by ID
    """
    try:
        contact = ContactController.get_contact(
            company_id=company_id,
            contact_id=contact_id,
            current_user=current_user,
            db=db
        )
        
        return success_response(
            data=contact.to_dict(include_relations=True),
            message="Contact retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving contact: {str(e)}"
        )


@router.put("/{company_id}/contacts/{contact_id}", response_model=dict)
async def update_contact(
    company_id: int = Path(..., description="Company ID"),
    contact_id: int = Path(..., description="Contact ID"),
    contact_data: ContactUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update contact
    """
    try:
        contact = ContactController.update_contact(
            company_id=company_id,
            contact_id=contact_id,
            contact_data=contact_data,
            current_user=current_user,
            db=db
        )
        
        return success_response(
            data=contact.to_dict(include_relations=True),
            message="Contact updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating contact: {str(e)}"
        )


@router.delete("/{company_id}/contacts/{contact_id}", response_model=dict)
async def delete_contact(
    company_id: int = Path(..., description="Company ID"),
    contact_id: int = Path(..., description="Contact ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete contact
    """
    try:
        ContactController.delete_contact(
            company_id=company_id,
            contact_id=contact_id,
            current_user=current_user,
            db=db
        )
        
        return success_response(
            data=None,
            message="Contact deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting contact: {str(e)}"
        )

