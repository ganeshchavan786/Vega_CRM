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


# Contact Role Management Endpoints

@router.put("/{company_id}/contacts/{contact_id}/role")
async def update_contact_role(
    company_id: int = Path(..., description="Company ID"),
    contact_id: int = Path(..., description="Contact ID"),
    role: str = Query(..., description="New role: decision_maker, influencer, user, gatekeeper, champion, economic_buyer"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update contact role
    
    Path Parameters:
    - **company_id**: Company ID
    - **contact_id**: Contact ID
    
    Query Parameters:
    - **role**: New role (decision_maker, influencer, user, gatekeeper, champion, economic_buyer)
    """
    from app.models.contact import Contact
    
    valid_roles = ["decision_maker", "influencer", "user", "gatekeeper", "champion", "economic_buyer"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    try:
        contact = ContactController.get_contact(company_id, contact_id, current_user, db)
        old_role = contact.role
        contact.role = role
        db.commit()
        db.refresh(contact)
        
        return success_response(
            data={
                "id": contact.id,
                "name": contact.name,
                "old_role": old_role,
                "new_role": role
            },
            message=f"Contact role updated from {old_role} to {role}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating contact role: {str(e)}"
        )


@router.put("/{company_id}/contacts/{contact_id}/set-primary")
async def set_primary_contact(
    company_id: int = Path(..., description="Company ID"),
    contact_id: int = Path(..., description="Contact ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Set contact as primary contact for account
    
    Path Parameters:
    - **company_id**: Company ID
    - **contact_id**: Contact ID
    """
    from app.models.contact import Contact
    
    try:
        contact = ContactController.get_contact(company_id, contact_id, current_user, db)
        
        # Unset other primary contacts for this account
        db.query(Contact).filter(
            Contact.account_id == contact.account_id,
            Contact.id != contact_id,
            Contact.is_primary_contact == True
        ).update({"is_primary_contact": False})
        
        # Set this contact as primary
        contact.is_primary_contact = True
        db.commit()
        db.refresh(contact)
        
        return success_response(
            data=contact.to_dict(),
            message=f"Contact '{contact.name}' set as primary contact"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting primary contact: {str(e)}"
        )


@router.get("/{company_id}/contacts/by-role")
async def get_contacts_by_role(
    company_id: int = Path(..., description="Company ID"),
    role: str = Query(..., description="Filter by role"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get contacts filtered by role
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **role**: Role to filter by
    """
    from app.models.contact import Contact
    from app.models.user_company import UserCompany
    
    # Check access
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id
    ).first()
    
    if not user_company and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        contacts = db.query(Contact).filter(
            Contact.company_id == company_id,
            Contact.role == role
        ).all()
        
        return success_response(
            data=[c.to_dict() for c in contacts],
            message=f"Found {len(contacts)} contacts with role '{role}'"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching contacts: {str(e)}"
        )


@router.get("/{company_id}/contacts/role-analytics")
async def get_contact_role_analytics(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get contact role analytics
    
    Returns:
    - Contact count by role
    - Role distribution
    - Influence score averages
    """
    from sqlalchemy import func
    from app.models.contact import Contact
    from app.models.user_company import UserCompany
    
    # Check access
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id
    ).first()
    
    if not user_company and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Total contacts
        total = db.query(func.count(Contact.id)).filter(
            Contact.company_id == company_id
        ).scalar() or 0
        
        # Contacts by role
        roles = ["decision_maker", "influencer", "user", "gatekeeper", "champion", "economic_buyer"]
        role_counts = {}
        for role in roles:
            count = db.query(func.count(Contact.id)).filter(
                Contact.company_id == company_id,
                Contact.role == role
            ).scalar() or 0
            role_counts[role] = count
        
        # Primary contacts count
        primary_count = db.query(func.count(Contact.id)).filter(
            Contact.company_id == company_id,
            Contact.is_primary_contact == True
        ).scalar() or 0
        
        # Average influence score by role
        influence_by_role = {}
        for role in roles:
            avg = db.query(func.avg(Contact.influence_score)).filter(
                Contact.company_id == company_id,
                Contact.role == role
            ).scalar()
            influence_by_role[role] = round(float(avg), 2) if avg else 0
        
        return success_response(
            data={
                "total_contacts": total,
                "by_role": role_counts,
                "primary_contacts": primary_count,
                "influence_by_role": influence_by_role,
                "role_distribution": {
                    role: round((count / total * 100), 2) if total > 0 else 0
                    for role, count in role_counts.items()
                }
            },
            message="Contact role analytics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching role analytics: {str(e)}"
        )

