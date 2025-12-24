"""
Email Sequence Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.email_sequence import EmailSequenceCreate, EmailSequenceUpdate, EmailSequenceResponse, EmailSequenceStatus
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User
from app.models.email_sequence import EmailSequence, EmailSequenceEmail
from app.models.lead import Lead

router = APIRouter()


@router.get("/{company_id}/email-sequences")
async def get_email_sequences(
    company_id: int = Path(..., description="Company ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all email sequences for company"""
    try:
        query = db.query(EmailSequence).filter(EmailSequence.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(EmailSequence.is_active == is_active)
        
        sequences = query.order_by(EmailSequence.created_at.desc()).all()
        
        return success_response(
            data=[seq.to_dict() for seq in sequences],
            message="Email sequences retrieved"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting email sequences: {str(e)}"
        )


@router.post("/{company_id}/email-sequences", status_code=status.HTTP_201_CREATED)
async def create_email_sequence(
    company_id: int = Path(..., description="Company ID"),
    sequence_data: EmailSequenceCreate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new email sequence"""
    try:
        new_sequence = EmailSequence(
            company_id=company_id,
            **sequence_data.model_dump()
        )
        
        db.add(new_sequence)
        db.commit()
        db.refresh(new_sequence)
        
        return success_response(
            data=new_sequence.to_dict(),
            message="Email sequence created successfully"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating email sequence: {str(e)}"
        )


@router.get("/{company_id}/email-sequences/{sequence_id}")
async def get_email_sequence(
    company_id: int = Path(..., description="Company ID"),
    sequence_id: int = Path(..., description="Sequence ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get email sequence by ID"""
    try:
        sequence = db.query(EmailSequence).filter(
            EmailSequence.id == sequence_id,
            EmailSequence.company_id == company_id
        ).first()
        
        if not sequence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email sequence not found"
            )
        
        return success_response(
            data=sequence.to_dict(),
            message="Email sequence retrieved"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting email sequence: {str(e)}"
        )


@router.put("/{company_id}/email-sequences/{sequence_id}")
async def update_email_sequence(
    company_id: int = Path(..., description="Company ID"),
    sequence_id: int = Path(..., description="Sequence ID"),
    sequence_data: EmailSequenceUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update email sequence"""
    try:
        sequence = db.query(EmailSequence).filter(
            EmailSequence.id == sequence_id,
            EmailSequence.company_id == company_id
        ).first()
        
        if not sequence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email sequence not found"
            )
        
        update_data = sequence_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(sequence, key, value)
        
        db.commit()
        db.refresh(sequence)
        
        return success_response(
            data=sequence.to_dict(),
            message="Email sequence updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating email sequence: {str(e)}"
        )


@router.post("/{company_id}/leads/{lead_id}/start-email-sequence")
async def start_email_sequence(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    sequence_id: Optional[int] = Query(None, description="Sequence ID (uses default if not provided)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start email sequence for a lead"""
    try:
        from app.utils.email_sequences import EmailSequenceAutomation
        
        result = EmailSequenceAutomation.start_sequence_for_lead(
            lead_id, company_id, sequence_id, db
        )
        
        return success_response(
            data=result,
            message=result.get("message", "Email sequence started")
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting email sequence: {str(e)}"
        )


@router.get("/{company_id}/leads/{lead_id}/email-sequence-status")
async def get_email_sequence_status(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get email sequence status for lead"""
    try:
        from app.utils.email_sequences import EmailSequenceAutomation
        
        status_data = EmailSequenceAutomation.get_sequence_status(
            lead_id, company_id, db
        )
        
        return success_response(
            data=status_data,
            message="Email sequence status retrieved"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting email sequence status: {str(e)}"
        )


@router.post("/{company_id}/email-sequences/track-open/{email_id}")
async def track_email_open(
    company_id: int = Path(..., description="Company ID"),
    email_id: int = Path(..., description="Email Sequence Email ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Track email open event (+5 points to lead score)
    
    This endpoint is typically called by email tracking pixel
    """
    try:
        from app.utils.email_sequences import EmailSequenceAutomation
        
        success = EmailSequenceAutomation.track_email_open(email_id, db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        return success_response(
            data={"tracked": True},
            message="Email open tracked"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking email open: {str(e)}"
        )


@router.post("/{company_id}/email-sequences/track-click/{email_id}")
async def track_email_click(
    company_id: int = Path(..., description="Company ID"),
    email_id: int = Path(..., description="Email Sequence Email ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Track email click event (+10 points to lead score)
    
    This endpoint is typically called when user clicks link in email
    """
    try:
        from app.utils.email_sequences import EmailSequenceAutomation
        
        success = EmailSequenceAutomation.track_email_click(email_id, db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        return success_response(
            data={"tracked": True},
            message="Email click tracked"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking email click: {str(e)}"
        )


@router.get("/{company_id}/email-sequences/pending-emails")
async def get_pending_emails(
    company_id: int = Path(..., description="Company ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of emails"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get pending emails ready to send
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        from app.utils.email_sequences import EmailSequenceAutomation
        from app.models.user_company import UserCompany
        
        # Check permission
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
        
        pending = EmailSequenceAutomation.get_pending_emails(company_id, db, limit)
        
        return success_response(
            data=[email.to_dict() for email in pending],
            message=f"Found {len(pending)} pending emails"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting pending emails: {str(e)}"
        )

