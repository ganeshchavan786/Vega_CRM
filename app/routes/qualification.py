"""
Lead Qualification Routes
Handles BANT/MEDDICC qualification, risk scoring, and conversion triggers
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


# Qualification Workflow Endpoints

@router.get("/{company_id}/leads/{lead_id}/qualification-score")
async def get_lead_qualification_score(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get BANT qualification score for a lead
    
    Returns:
    - Total score (0-100)
    - Score breakdown (Budget, Authority, Need, Timeline)
    - Qualification status
    """
    from app.services.qualification_service import QualificationService
    from app.models.lead import Lead
    
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.company_id == company_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    try:
        score = QualificationService.calculate_bant_score(lead)
        return success_response(
            data={"lead_id": lead_id, "lead_name": lead.lead_name, **score},
            message="Qualification score calculated"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating score: {str(e)}"
        )


@router.post("/{company_id}/leads/{lead_id}/qualify")
async def qualify_lead(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Qualify a lead and update its status based on BANT score
    """
    from app.services.qualification_service import QualificationService
    
    try:
        result = QualificationService.qualify_lead(lead_id, company_id, db, current_user.id)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to qualify lead")
            )
        return success_response(
            data=result,
            message="Lead qualification complete"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error qualifying lead: {str(e)}"
        )


@router.get("/{company_id}/leads/{lead_id}/qualification-checklist")
async def get_qualification_checklist(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get qualification checklist for a lead
    """
    from app.services.qualification_service import QualificationService
    from app.models.lead import Lead
    
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.company_id == company_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    try:
        checklist = QualificationService.get_qualification_checklist(lead)
        return success_response(
            data={"lead_id": lead_id, **checklist},
            message="Qualification checklist fetched"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching checklist: {str(e)}"
        )


@router.get("/{company_id}/qualification/analytics")
async def get_qualification_analytics(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get qualification analytics for company
    """
    from app.services.qualification_service import QualificationService
    
    try:
        analytics = QualificationService.get_qualification_analytics(company_id, db)
        return success_response(
            data=analytics,
            message="Qualification analytics fetched"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analytics: {str(e)}"
        )


@router.post("/{company_id}/qualification/batch-qualify")
async def batch_qualify_leads(
    company_id: int = Path(..., description="Company ID"),
    lead_ids: Optional[List[int]] = Query(None, description="List of lead IDs"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Batch qualify multiple leads
    """
    from app.services.qualification_service import QualificationService
    from app.models.user_company import UserCompany
    
    # Check admin/manager permission
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.role.in_(["admin", "manager"])
    ).first()
    
    if not user_company and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin/Manager permission required"
        )
    
    try:
        result = QualificationService.batch_qualify_leads(company_id, db, lead_ids)
        return success_response(
            data=result,
            message=f"Batch qualification complete: {result['qualified']} qualified"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch qualification: {str(e)}"
        )


# Risk Scoring Endpoints

@router.get("/{company_id}/leads/{lead_id}/risk-score")
async def get_lead_risk_score(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get risk score for a lead
    
    Returns:
    - Risk score (0-100, higher = lower risk)
    - Risk level (low, medium, high, critical)
    - Risk factors and recommendations
    """
    from app.services.risk_scoring_service import RiskScoringService
    
    try:
        result = RiskScoringService.update_lead_risk_score(lead_id, company_id, db)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Lead not found")
            )
        return success_response(
            data=result,
            message="Risk score calculated"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating risk score: {str(e)}"
        )


@router.get("/{company_id}/risk/high-risk-leads")
async def get_high_risk_leads(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all high and critical risk leads
    """
    from app.services.risk_scoring_service import RiskScoringService
    
    try:
        leads = RiskScoringService.get_high_risk_leads(company_id, db)
        return success_response(
            data={"high_risk_leads": leads, "count": len(leads)},
            message=f"Found {len(leads)} high risk leads"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching high risk leads: {str(e)}"
        )


@router.get("/{company_id}/risk/analytics")
async def get_risk_analytics(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get risk analytics for company
    """
    from app.services.risk_scoring_service import RiskScoringService
    
    try:
        analytics = RiskScoringService.get_risk_analytics(company_id, db)
        return success_response(
            data=analytics,
            message="Risk analytics fetched"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching risk analytics: {str(e)}"
        )


@router.post("/{company_id}/risk/batch-update")
async def batch_update_risk_scores(
    company_id: int = Path(..., description="Company ID"),
    lead_ids: Optional[List[int]] = Query(None, description="List of lead IDs"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Batch update risk scores for multiple leads
    """
    from app.services.risk_scoring_service import RiskScoringService
    
    try:
        result = RiskScoringService.batch_update_risk_scores(company_id, db, lead_ids)
        return success_response(
            data=result,
            message=f"Batch risk update complete for {result['total']} leads"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch update: {str(e)}"
        )


# Conversion Trigger Endpoints

@router.get("/{company_id}/leads/{lead_id}/conversion-eligibility")
async def check_conversion_eligibility(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check if a lead is eligible for conversion
    
    Returns:
    - Eligibility status
    - Criteria breakdown
    - Blocking issues
    """
    from app.services.conversion_trigger_service import ConversionTriggerService
    from app.models.lead import Lead
    
    lead = db.query(Lead).filter(
        Lead.id == lead_id,
        Lead.company_id == company_id
    ).first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    try:
        eligibility = ConversionTriggerService.check_conversion_eligibility(lead, db)
        return success_response(
            data={"lead_id": lead_id, "lead_name": lead.lead_name, **eligibility},
            message="Conversion eligibility checked"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking eligibility: {str(e)}"
        )


@router.get("/{company_id}/conversion/ready-leads")
async def get_conversion_ready_leads(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all leads ready for conversion
    """
    from app.services.conversion_trigger_service import ConversionTriggerService
    
    try:
        leads = ConversionTriggerService.get_conversion_ready_leads(company_id, db)
        return success_response(
            data={"ready_leads": leads, "count": len(leads)},
            message=f"Found {len(leads)} conversion-ready leads"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ready leads: {str(e)}"
        )


@router.post("/{company_id}/leads/{lead_id}/auto-convert")
async def auto_convert_lead(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Automatically convert an eligible lead
    """
    from app.services.conversion_trigger_service import ConversionTriggerService
    
    try:
        result = ConversionTriggerService.auto_trigger_conversion(
            lead_id, company_id, current_user.id, db
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Conversion failed")
            )
        return success_response(
            data=result,
            message="Lead converted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting lead: {str(e)}"
        )


@router.post("/{company_id}/conversion/batch-check")
async def batch_check_conversion_triggers(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Batch check conversion triggers for all leads
    """
    from app.services.conversion_trigger_service import ConversionTriggerService
    
    try:
        result = ConversionTriggerService.batch_check_conversion_triggers(company_id, db)
        return success_response(
            data=result,
            message=f"Checked {result['total_checked']} leads, {result['eligible_for_conversion']} eligible"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch check: {str(e)}"
        )


@router.get("/{company_id}/conversion/analytics")
async def get_conversion_analytics(
    company_id: int = Path(..., description="Company ID"),
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get conversion analytics
    """
    from app.services.conversion_trigger_service import ConversionTriggerService
    
    try:
        analytics = ConversionTriggerService.get_conversion_analytics(company_id, db, days)
        return success_response(
            data=analytics,
            message="Conversion analytics fetched"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analytics: {str(e)}"
        )


@router.post("/{company_id}/leads/{lead_id}/conversion-reminder")
async def set_conversion_reminder(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    days_delay: int = Query(3, ge=1, le=14, description="Days until reminder"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Set a reminder for lead conversion
    """
    from app.services.conversion_trigger_service import ConversionTriggerService
    
    try:
        result = ConversionTriggerService.set_conversion_reminder(
            lead_id, company_id, current_user.id, db, days_delay
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to set reminder")
            )
        return success_response(
            data=result,
            message="Conversion reminder set"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting reminder: {str(e)}"
        )
