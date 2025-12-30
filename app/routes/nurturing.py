"""
Lead Nurturing Routes
Handles email sequence automation, task automation, WhatsApp integration, and engagement tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


# Email Sequence Automation Endpoints

@router.get("/{company_id}/email-sequences/analytics")
async def get_email_sequence_analytics(
    company_id: int = Path(..., description="Company ID"),
    sequence_id: Optional[int] = Query(None, description="Specific sequence ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get email sequence analytics
    
    Returns:
    - Total sequences and active count
    - Email metrics (sent, opens, clicks, replies)
    - Open rate, click rate, reply rate
    """
    from app.services.email_sequence_service import EmailSequenceService
    
    try:
        analytics = EmailSequenceService.get_sequence_analytics(company_id, sequence_id, db)
        return success_response(
            data=analytics,
            message="Email sequence analytics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analytics: {str(e)}"
        )


@router.post("/{company_id}/email-sequences/{sequence_id}/start/{lead_id}")
async def start_sequence_for_lead(
    company_id: int = Path(..., description="Company ID"),
    sequence_id: int = Path(..., description="Sequence ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Start an email sequence for a specific lead
    """
    from app.services.email_sequence_service import EmailSequenceService
    
    try:
        result = EmailSequenceService.start_sequence_for_lead(lead_id, sequence_id, company_id, db)
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to start sequence")
            )
        return success_response(
            data=result,
            message="Email sequence started for lead"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting sequence: {str(e)}"
        )


@router.post("/{company_id}/email-sequences/track-event")
async def track_email_event(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Query(..., description="Lead ID"),
    event_type: str = Query(..., description="Event type: open, click, reply, bounce, unsubscribe"),
    email_id: Optional[str] = Query(None, description="Email identifier"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Track email engagement event and update lead score
    
    Event types:
    - open: +5 points
    - click: +10 points
    - reply: +15 points
    - bounce: -5 points
    - unsubscribe: -10 points
    """
    from app.services.email_sequence_service import EmailSequenceService
    
    valid_events = ["open", "click", "reply", "bounce", "unsubscribe"]
    if event_type not in valid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event type. Must be one of: {', '.join(valid_events)}"
        )
    
    try:
        result = EmailSequenceService.track_email_event(lead_id, company_id, event_type, email_id, db)
        return success_response(
            data=result,
            message=f"Email {event_type} event tracked"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking event: {str(e)}"
        )


@router.get("/{company_id}/email-sequences/pending")
async def get_pending_emails(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get pending emails to be sent
    """
    from app.services.email_sequence_service import EmailSequenceService
    
    try:
        pending = EmailSequenceService.get_pending_emails(company_id, db)
        return success_response(
            data={"pending_emails": pending, "count": len(pending)},
            message=f"Found {len(pending)} pending emails"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching pending emails: {str(e)}"
        )


# Task Automation Endpoints

@router.post("/{company_id}/tasks/auto-create-followup")
async def auto_create_followup_task(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Query(..., description="Lead ID"),
    days_delay: int = Query(7, ge=1, le=30, description="Days until due date"),
    priority: str = Query("medium", description="Task priority"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create automatic follow-up task for a lead
    """
    from app.services.task_automation_service import TaskAutomationService
    
    try:
        result = TaskAutomationService.create_follow_up_task(
            lead_id=lead_id,
            company_id=company_id,
            user_id=current_user.id,
            db=db,
            days_delay=days_delay,
            priority=priority
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create task")
            )
        return success_response(
            data=result,
            message="Follow-up task created"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )


@router.get("/{company_id}/tasks/overdue")
async def get_overdue_tasks(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get overdue tasks for escalation
    """
    from app.services.task_automation_service import TaskAutomationService
    
    try:
        overdue = TaskAutomationService.get_overdue_tasks(company_id, db)
        return success_response(
            data={"overdue_tasks": overdue, "count": len(overdue)},
            message=f"Found {len(overdue)} overdue tasks"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching overdue tasks: {str(e)}"
        )


@router.post("/{company_id}/tasks/escalate-overdue")
async def escalate_overdue_tasks(
    company_id: int = Path(..., description="Company ID"),
    escalation_days: int = Query(3, ge=1, le=14, description="Days overdue to trigger escalation"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Escalate tasks overdue by specified days
    """
    from app.services.task_automation_service import TaskAutomationService
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
        result = TaskAutomationService.escalate_overdue_tasks(company_id, db, escalation_days)
        return success_response(
            data=result,
            message=f"Escalated {result['escalated']} tasks"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error escalating tasks: {str(e)}"
        )


@router.post("/{company_id}/tasks/auto-create-for-leads")
async def auto_create_tasks_for_leads(
    company_id: int = Path(..., description="Company ID"),
    days_since_creation: int = Query(7, ge=1, le=30, description="Days since lead creation"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Auto-create follow-up tasks for leads without recent tasks
    """
    from app.services.task_automation_service import TaskAutomationService
    
    try:
        result = TaskAutomationService.auto_create_tasks_for_new_leads(company_id, db, days_since_creation)
        return success_response(
            data=result,
            message=f"Created {result['tasks_created']} tasks"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating tasks: {str(e)}"
        )


@router.get("/{company_id}/tasks/automation-stats")
async def get_task_automation_stats(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get task automation statistics
    """
    from app.services.task_automation_service import TaskAutomationService
    
    try:
        stats = TaskAutomationService.get_task_automation_stats(company_id, db)
        return success_response(
            data=stats,
            message="Task automation stats fetched"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )


# WhatsApp Integration Endpoints

@router.post("/{company_id}/whatsapp/send")
async def send_whatsapp_message(
    company_id: int = Path(..., description="Company ID"),
    phone: str = Query(..., description="Recipient phone number"),
    message: str = Query(..., description="Message content"),
    lead_id: Optional[int] = Query(None, description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send WhatsApp message
    """
    from app.services.whatsapp_service import WhatsAppService
    
    try:
        result = WhatsAppService.send_message(
            phone=phone,
            message=message,
            lead_id=lead_id,
            company_id=company_id,
            user_id=current_user.id,
            db=db
        )
        return success_response(
            data=result,
            message="WhatsApp message sent"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending message: {str(e)}"
        )


@router.post("/{company_id}/whatsapp/send-template")
async def send_whatsapp_template(
    company_id: int = Path(..., description="Company ID"),
    phone: str = Query(..., description="Recipient phone number"),
    template_name: str = Query(..., description="Template name: welcome, follow_up, reminder"),
    lead_id: Optional[int] = Query(None, description="Lead ID"),
    name: Optional[str] = Query(None, description="Recipient name for template"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send WhatsApp template message
    """
    from app.services.whatsapp_service import WhatsAppService
    
    try:
        variables = {"name": name} if name else {}
        result = WhatsAppService.send_template_message(
            phone=phone,
            template_name=template_name,
            lead_id=lead_id,
            company_id=company_id,
            user_id=current_user.id,
            db=db,
            variables=variables
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to send template")
            )
        return success_response(
            data=result,
            message="WhatsApp template sent"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending template: {str(e)}"
        )


@router.post("/{company_id}/whatsapp/webhook/incoming")
async def whatsapp_incoming_webhook(
    company_id: int = Path(..., description="Company ID"),
    phone: str = Query(..., description="Sender phone"),
    message: str = Query(..., description="Message content"),
    db: Session = Depends(get_db)
):
    """
    Webhook for incoming WhatsApp messages
    """
    from app.services.whatsapp_service import WhatsAppService
    
    try:
        result = WhatsAppService.handle_incoming_message(phone, message, company_id, db)
        return success_response(
            data=result,
            message="Incoming message processed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/{company_id}/whatsapp/schedule-followups")
async def schedule_whatsapp_followups(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Query(..., description="Lead ID"),
    delay_days: int = Query(3, ge=1, le=14, description="Days between messages"),
    num_messages: int = Query(2, ge=1, le=5, description="Number of follow-up messages"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Schedule follow-up WhatsApp messages for a lead
    """
    from app.services.whatsapp_service import WhatsAppService
    
    try:
        result = WhatsAppService.schedule_follow_up_messages(
            lead_id=lead_id,
            company_id=company_id,
            db=db,
            delay_days=delay_days,
            num_messages=num_messages
        )
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to schedule")
            )
        return success_response(
            data=result,
            message="WhatsApp follow-ups scheduled"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling: {str(e)}"
        )


@router.get("/{company_id}/whatsapp/analytics")
async def get_whatsapp_analytics(
    company_id: int = Path(..., description="Company ID"),
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get WhatsApp messaging analytics
    """
    from app.services.whatsapp_service import WhatsAppService
    
    try:
        analytics = WhatsAppService.get_whatsapp_analytics(company_id, db, days)
        return success_response(
            data=analytics,
            message="WhatsApp analytics fetched"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analytics: {str(e)}"
        )


@router.get("/{company_id}/whatsapp/opt-in-status")
async def check_whatsapp_opt_in(
    company_id: int = Path(..., description="Company ID"),
    phone: str = Query(..., description="Phone number to check"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check WhatsApp opt-in status for a phone number
    """
    from app.services.whatsapp_service import WhatsAppService
    
    try:
        status = WhatsAppService.get_opt_in_status(phone, company_id, db)
        return success_response(
            data=status,
            message="Opt-in status checked"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking opt-in: {str(e)}"
        )


# Score Increment Endpoints

@router.post("/{company_id}/leads/{lead_id}/increment-score")
async def increment_lead_score(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    increment: int = Query(..., ge=-50, le=50, description="Score increment (can be negative)"),
    reason: str = Query(..., description="Reason for increment"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Manually increment lead score
    """
    from app.utils.lead_scoring import LeadScoringAlgorithm
    
    try:
        new_score = LeadScoringAlgorithm.increment_lead_score(
            lead_id=lead_id,
            company_id=company_id,
            increment=increment,
            db=db,
            reason=reason
        )
        
        if new_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        return success_response(
            data={"lead_id": lead_id, "new_score": new_score, "increment": increment},
            message=f"Lead score updated by {increment:+d}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating score: {str(e)}"
        )


@router.post("/{company_id}/leads/batch-recalculate-scores")
async def batch_recalculate_scores(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Batch recalculate lead scores for all leads
    """
    from app.utils.lead_scoring import LeadScoringAlgorithm
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
        result = LeadScoringAlgorithm.batch_update_lead_scores(company_id, db)
        return success_response(
            data=result,
            message=f"Recalculated {result['updated']} lead scores"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalculating scores: {str(e)}"
        )
