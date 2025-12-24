"""
Lead Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.lead import LeadCreate, LeadUpdate
from app.controllers.lead_controller import LeadController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


@router.get("/{company_id}/leads")
async def get_leads(
    company_id: int = Path(..., description="Company ID"),
    search: Optional[str] = Query(None, description="Search in name/email/phone"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all leads in company"""
    try:
        leads = LeadController.get_leads(
            company_id, current_user, db, search, status, priority, assigned_to
        )
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_leads = leads[start:end]
        
        total = len(leads)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [lead.to_dict(include_relations=True) for lead in paginated_leads],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            },
            "message": "Leads fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/leads", status_code=status.HTTP_201_CREATED)
async def create_lead(
    company_id: int = Path(..., description="Company ID"),
    lead_data: LeadCreate = ...,
    skip_duplicate_check: bool = Query(False, description="Skip duplicate check (admin only)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new lead with duplicate detection
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **skip_duplicate_check**: Skip duplicate check (requires admin role)
    
    Requires: JWT token
    """
    try:
        # Check permission for skip_duplicate_check
        if skip_duplicate_check:
            from app.models.user_company import UserCompany
            user_company = db.query(UserCompany).filter(
                UserCompany.user_id == current_user.id,
                UserCompany.company_id == company_id,
                UserCompany.role.in_(["admin", "manager"])
            ).first()
            
            if not user_company and current_user.role != "super_admin":
                skip_duplicate_check = False  # Force duplicate check
        
        lead = LeadController.create_lead(
            company_id, lead_data, current_user, db, skip_duplicate_check=skip_duplicate_check
        )
        return success_response(
            data=lead.to_dict(include_relations=True),
            message="Lead created successfully"
        )
    except HTTPException as e:
        # Handle duplicate conflict specially
        if e.status_code == status.HTTP_409_CONFLICT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=e.detail
            )
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/leads/{lead_id}")
async def get_lead(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get lead details"""
    try:
        lead = LeadController.get_lead(lead_id, company_id, current_user, db)
        return success_response(
            data=lead.to_dict(include_relations=True),
            message="Lead details fetched successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/leads/{lead_id}")
async def update_lead(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    lead_data: LeadUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update lead"""
    try:
        lead = LeadController.update_lead(lead_id, company_id, lead_data, current_user, db)
        return success_response(
            data=lead.to_dict(include_relations=True),
            message="Lead updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{company_id}/leads/{lead_id}")
async def delete_lead(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete lead"""
    try:
        LeadController.delete_lead(lead_id, company_id, current_user, db)
        return success_response(
            data={},
            message="Lead deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/leads/{lead_id}/recalculate-score")
async def recalculate_lead_score(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Recalculate lead score for a specific lead
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Requires: JWT token
    """
    try:
        from app.utils.lead_scoring import LeadScoringAlgorithm
        
        new_score = LeadScoringAlgorithm.update_lead_score(
            lead_id, company_id, db, force_update=True
        )
        
        if new_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        return success_response(
            data={"lead_score": new_score, "category": LeadScoringAlgorithm.get_score_category(new_score)},
            message="Lead score recalculated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalculating lead score: {str(e)}"
        )


@router.post("/{company_id}/leads/{lead_id}/increment-score")
async def increment_lead_score(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    increment: int = Query(..., description="Points to add (can be negative)", ge=-100, le=100),
    reason: Optional[str] = Query(None, description="Reason for increment"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Increment lead score by a specific amount
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Query Parameters:
    - **increment**: Points to add (can be negative)
    - **reason**: Optional reason for increment
    
    Requires: JWT token
    """
    try:
        from app.utils.lead_scoring import LeadScoringAlgorithm
        
        new_score = LeadScoringAlgorithm.increment_lead_score(
            lead_id, company_id, increment, db, reason=reason
        )
        
        if new_score is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        return success_response(
            data={"lead_score": new_score, "category": LeadScoringAlgorithm.get_score_category(new_score)},
            message=f"Lead score incremented by {increment} points"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error incrementing lead score: {str(e)}"
        )


@router.post("/{company_id}/leads/batch-recalculate-scores")
async def batch_recalculate_lead_scores(
    company_id: int = Path(..., description="Company ID"),
    lead_ids: Optional[List[int]] = Query(None, description="List of lead IDs (optional, all if not provided)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Batch recalculate lead scores for multiple leads
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **lead_ids**: Optional list of lead IDs (all leads if not provided)
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        from app.utils.lead_scoring import LeadScoringAlgorithm
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
        
        result = LeadScoringAlgorithm.batch_update_lead_scores(
            company_id, db, lead_ids
        )
        
        return success_response(
            data=result,
            message=f"Lead scores recalculated: {result['updated']} updated, {result['unchanged']} unchanged"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recalculating lead scores: {str(e)}"
        )


@router.get("/{company_id}/leads/{lead_id}/check-duplicate")
async def check_duplicate(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check for duplicate leads for a specific lead
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Requires: JWT token
    """
    try:
        from app.utils.duplicate_detection import DuplicateDetectionEngine
        
        lead = LeadController.get_lead(lead_id, company_id, current_user, db)
        
        result = DuplicateDetectionEngine.check_duplicate(
            company_id=company_id,
            email=lead.email,
            phone=lead.phone,
            company_name=lead.company_name,
            db=db,
            exclude_lead_id=lead_id
        )
        
        return success_response(
            data={
                "is_duplicate": result["is_duplicate"],
                "duplicate_leads": [
                    {
                        "id": dup.id,
                        "name": dup.full_name,
                        "email": dup.email,
                        "phone": dup.phone,
                        "company_name": dup.company_name,
                        "created_at": dup.created_at.isoformat() if dup.created_at else None
                    }
                    for dup in result["duplicate_leads"]
                ],
                "match_reason": result["match_reason"],
                "confidence": result["confidence"],
                "match_count": result["match_count"]
            },
            message="Duplicate check completed"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking duplicates: {str(e)}"
        )


@router.post("/{company_id}/leads/detect-duplicates")
async def detect_duplicates(
    company_id: int = Path(..., description="Company ID"),
    auto_mark: bool = Query(False, description="Automatically mark duplicates"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Scan all leads and detect duplicates
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **auto_mark**: Automatically mark duplicates (requires admin role)
    
    Requires: JWT token, Admin/Manager role for auto_mark
    """
    try:
        from app.utils.duplicate_detection import DuplicateDetectionEngine
        from app.models.user_company import UserCompany
        
        # Check permission for auto_mark
        if auto_mark:
            user_company = db.query(UserCompany).filter(
                UserCompany.user_id == current_user.id,
                UserCompany.company_id == company_id,
                UserCompany.role.in_(["admin", "manager"])
            ).first()
            
            if not user_company and current_user.role != "super_admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for auto-marking duplicates"
                )
        
        result = DuplicateDetectionEngine.detect_and_mark_duplicates(
            company_id, db, auto_mark=auto_mark
        )
        
        return success_response(
            data=result,
            message=f"Duplicate detection completed: {result['duplicate_groups_found']} groups found"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error detecting duplicates: {str(e)}"
        )


@router.post("/{company_id}/leads/{lead_id}/mark-duplicate")
async def mark_duplicate(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    is_duplicate: bool = Query(True, description="Mark as duplicate (True) or unmark (False)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Mark or unmark lead as duplicate
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Query Parameters:
    - **is_duplicate**: True to mark as duplicate, False to unmark
    
    Requires: JWT token
    """
    try:
        from app.utils.duplicate_detection import DuplicateDetectionEngine
        
        success = DuplicateDetectionEngine.mark_as_duplicate(
            lead_id, company_id, db, is_duplicate=is_duplicate
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        return success_response(
            data={"is_duplicate": is_duplicate},
            message=f"Lead {'marked' if is_duplicate else 'unmarked'} as duplicate"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking duplicate: {str(e)}"
        )


@router.post("/{company_id}/leads/{primary_lead_id}/merge-duplicates")
async def merge_duplicates(
    company_id: int = Path(..., description="Company ID"),
    primary_lead_id: int = Path(..., description="Primary Lead ID (to keep)"),
    duplicate_lead_ids: List[int] = Query(..., description="List of duplicate lead IDs to merge"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Merge duplicate leads into primary lead
    
    Path Parameters:
    - **company_id**: Company ID
    - **primary_lead_id**: ID of lead to keep
    
    Query Parameters:
    - **duplicate_lead_ids**: List of duplicate lead IDs to merge
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        from app.utils.duplicate_detection import DuplicateDetectionEngine
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
        
        success = DuplicateDetectionEngine.merge_duplicates(
            primary_lead_id, duplicate_lead_ids, company_id, db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Primary lead not found"
            )
        
        return success_response(
            data={"merged_count": len(duplicate_lead_ids)},
            message=f"Successfully merged {len(duplicate_lead_ids)} duplicate leads"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error merging duplicates: {str(e)}"
        )


@router.get("/{company_id}/leads/assignment/stats")
async def get_assignment_stats(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get lead assignment statistics
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token
    """
    try:
        from app.utils.assignment_rules import AssignmentRulesEngine
        
        stats = AssignmentRulesEngine.get_assignment_stats(company_id, db)
        
        return success_response(
            data=stats,
            message="Assignment statistics retrieved"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting assignment stats: {str(e)}"
        )


@router.post("/{company_id}/leads/reassign")
async def reassign_leads(
    company_id: int = Path(..., description="Company ID"),
    rule_type: str = Query("round_robin", description="Assignment rule type"),
    dry_run: bool = Query(False, description="Dry run (don't actually reassign)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reassign unassigned leads based on assignment rule
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **rule_type**: Assignment rule type (round_robin, territory_based, load_balanced)
    - **dry_run**: If True, don't actually reassign
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        from app.utils.assignment_rules import AssignmentRulesEngine, AssignmentRuleType
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
        
        # Validate rule type
        valid_rules = [AssignmentRuleType.ROUND_ROBIN, AssignmentRuleType.TERRITORY_BASED, AssignmentRuleType.LOAD_BALANCED]
        if rule_type not in valid_rules:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid rule_type. Must be one of: {', '.join(valid_rules)}"
            )
        
        result = AssignmentRulesEngine.reassign_leads(
            company_id=company_id,
            rule_type=rule_type,
            db=db,
            dry_run=dry_run
        )
        
        return success_response(
            data=result,
            message=f"Reassignment {'plan' if dry_run else 'completed'}: {result['reassigned_count']} leads"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reassigning leads: {str(e)}"
        )


@router.get("/{company_id}/leads/{lead_id}/check-conversion-eligibility")
async def check_conversion_eligibility(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check if lead is eligible for conversion
    
    Conversion Trigger:
    IF Lead Score > 70 AND Lead Status = "Contacted"
    THEN Allow Conversion
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Requires: JWT token
    """
    try:
        from app.utils.nurturing_automation import NurturingAutomation
        
        result = NurturingAutomation.check_conversion_eligibility(
            lead_id, company_id, db
        )
        
        return success_response(
            data=result,
            message="Conversion eligibility checked"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking conversion eligibility: {str(e)}"
        )


@router.post("/{company_id}/leads/{lead_id}/create-followup-task")
async def create_followup_task(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create follow-up task for lead (if eligible)
    
    Rules:
    - Lead must be 7+ days old
    - Lead must be active (not converted/disqualified)
    - Lead must have assigned owner
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Requires: JWT token
    """
    try:
        from app.utils.nurturing_automation import NurturingAutomation
        
        task = NurturingAutomation.check_and_create_followup_task(
            lead_id, company_id, db
        )
        
        if not task:
            return success_response(
                data={"task_created": False},
                message="Follow-up task not created (lead may be too new, already has task, or is inactive)"
            )
        
        return success_response(
            data=task.to_dict(include_relations=True),
            message="Follow-up task created successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating follow-up task: {str(e)}"
        )


@router.post("/{company_id}/leads/process-nurturing-tasks")
async def process_nurturing_tasks(
    company_id: int = Path(..., description="Company ID"),
    dry_run: bool = Query(False, description="Dry run (don't create tasks, just return plan)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process all leads and create follow-up tasks where needed
    
    Path Parameters:
    - **company_id**: Company ID
    
    Query Parameters:
    - **dry_run**: If True, don't create tasks, just return plan
    
    Requires: JWT token, Admin/Manager role
    """
    try:
        from app.utils.nurturing_automation import NurturingAutomation
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
        
        result = NurturingAutomation.process_nurturing_tasks(
            company_id, db, dry_run=dry_run
        )
        
        return success_response(
            data=result,
            message=f"Nurturing tasks processed: {result['tasks_created']} tasks created"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing nurturing tasks: {str(e)}"
        )


@router.get("/{company_id}/leads/nurturing/stats")
async def get_nurturing_stats(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get nurturing statistics for company
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token
    """
    try:
        from app.utils.nurturing_automation import NurturingAutomation
        
        stats = NurturingAutomation.get_nurturing_stats(company_id, db)
        
        return success_response(
            data=stats,
            message="Nurturing statistics retrieved"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting nurturing stats: {str(e)}"
        )


@router.get("/{company_id}/leads/{lead_id}/conversion-preview")
async def get_conversion_preview(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get preview of what will be created during conversion
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Requires: JWT token
    """
    try:
        from app.utils.lead_conversion import LeadConversionService
        
        preview = LeadConversionService.get_conversion_preview(
            lead_id, company_id, db
        )
        
        return success_response(
            data=preview,
            message="Conversion preview generated"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating conversion preview: {str(e)}"
        )


@router.post("/{company_id}/leads/{lead_id}/convert")
async def convert_lead(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    skip_eligibility_check: bool = Query(False, description="Skip eligibility check (admin only)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Convert lead to account (Account-First Model)
    
    Process:
    1. Create Account (Customer) from Lead
    2. Create Contact from Lead
    3. Link Contact to Account
    4. Create Opportunity (Deal) from Lead
    5. Log Initial Activity
    6. Update Lead status to "Converted"
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Query Parameters:
    - **skip_eligibility_check**: Skip eligibility check (requires admin role)
    
    Requires: JWT token
    """
    try:
        from app.utils.lead_conversion import LeadConversionService
        from app.models.user_company import UserCompany
        
        # Check permission for skip_eligibility_check
        if skip_eligibility_check:
            user_company = db.query(UserCompany).filter(
                UserCompany.user_id == current_user.id,
                UserCompany.company_id == company_id,
                UserCompany.role.in_(["admin", "manager"])
            ).first()
            
            if not user_company and current_user.role != "super_admin":
                skip_eligibility_check = False  # Force eligibility check
        
        result = LeadConversionService.convert_lead_to_account(
            lead_id, company_id, current_user, db, skip_eligibility_check=skip_eligibility_check
        )
        
        return success_response(
            data=result,
            message="Lead converted successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting lead: {str(e)}"
        )


@router.get("/{company_id}/leads/{lead_id}/qualification")
async def get_lead_qualification(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get BANT/MEDDICC qualification summary for lead
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Requires: JWT token
    """
    try:
        from app.utils.qualification_scoring import QualificationScoring
        
        lead = LeadController.get_lead(lead_id, company_id, current_user, db)
        
        qualification = QualificationScoring.get_qualification_summary(lead)
        
        return success_response(
            data=qualification,
            message="Qualification summary retrieved"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting qualification: {str(e)}"
        )


@router.get("/{company_id}/leads/{lead_id}/can-convert")
async def can_convert_lead(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check if lead can be converted (legacy endpoint, use check-conversion-eligibility)
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Requires: JWT token
    """
    try:
        from app.utils.nurturing_automation import NurturingAutomation
        
        result = NurturingAutomation.check_conversion_eligibility(
            lead_id, company_id, db
        )
        
        return success_response(
            data={"can_convert": result["eligible"], **result},
            message="Conversion eligibility checked"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking conversion eligibility: {str(e)}"
        )
async def check_can_convert(
    company_id: int = Path(..., description="Company ID"),
    lead_id: int = Path(..., description="Lead ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check if lead can be converted based on score and status
    
    Rule: Lead Score >= 70 AND Status = "Contacted"
    
    Path Parameters:
    - **company_id**: Company ID
    - **lead_id**: Lead ID
    
    Requires: JWT token
    """
    try:
        from app.utils.lead_scoring import LeadScoringAlgorithm
        
        lead = LeadController.get_lead(lead_id, company_id, current_user, db)
        
        can_convert = LeadScoringAlgorithm.can_convert(lead)
        
        return success_response(
            data={
                "can_convert": can_convert,
                "lead_score": lead.lead_score or 0,
                "status": lead.status,
                "reason": "Lead score >= 70 and status is 'contacted'" if can_convert else 
                         f"Lead score is {lead.lead_score or 0} (need >= 70) or status is '{lead.status}' (need 'contacted')"
            },
            message="Conversion eligibility checked"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking conversion eligibility: {str(e)}"
        )


@router.get("/{company_id}/leads-stats")
async def get_lead_stats(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get lead statistics"""
    try:
        stats = LeadController.get_lead_stats(company_id, db)
        return success_response(
            data=stats,
            message="Lead statistics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

