"""
Lead Controller
Handles lead management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.lead import Lead
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.lead import LeadCreate, LeadUpdate
from app.utils.lead_scoring import LeadScoringAlgorithm
from app.utils.duplicate_detection import DuplicateDetectionEngine
from app.utils.assignment_rules import AssignmentRulesEngine, AssignmentRuleType
from app.utils.nurturing_automation import NurturingAutomation
from app.services import audit_service, log_service


class LeadController:
    """Lead management business logic"""
    
    @staticmethod
    def get_leads(
        company_id: int,
        current_user: User,
        db: Session,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[int] = None
    ) -> List[Lead]:
        """Get all leads in company"""
        query = db.query(Lead).filter(Lead.company_id == company_id)
        
        if search:
            query = query.filter(
                (Lead.lead_name.contains(search)) |
                (Lead.email.contains(search)) |
                (Lead.phone.contains(search))
            )
        
        if status:
            query = query.filter(Lead.status == status)
        
        if priority:
            query = query.filter(Lead.priority == priority)
        
        if assigned_to:
            query = query.filter(Lead.assigned_to == assigned_to)
        
        leads = query.order_by(Lead.created_at.desc()).all()
        return leads
    
    @staticmethod
    def create_lead(
        company_id: int,
        lead_data: LeadCreate,
        current_user: User,
        db: Session,
        skip_duplicate_check: bool = False
    ) -> Lead:
        """
        Create new lead with duplicate detection
        
        Args:
            company_id: Company ID
            lead_data: Lead creation data
            current_user: Current user
            db: Database session
            skip_duplicate_check: Skip duplicate check (for admin/import)
            
        Returns:
            Created lead
            
        Raises:
            HTTPException: If duplicate found and not allowed
        """
        # Check for duplicates before creating
        if not skip_duplicate_check:
            duplicate_check = DuplicateDetectionEngine.check_duplicate(
                company_id=company_id,
                email=lead_data.email,
                phone=lead_data.phone,
                company_name=lead_data.company_name,
                db=db
            )
            
            if duplicate_check["is_duplicate"]:
                # Raise exception with duplicate information
                duplicate_ids = [lead.id for lead in duplicate_check["duplicate_leads"]]
                duplicate_names = [lead.full_name for lead in duplicate_check["duplicate_leads"]]
                
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Duplicate lead detected",
                        "duplicate_lead_ids": duplicate_ids,
                        "duplicate_lead_names": duplicate_names,
                        "match_reason": duplicate_check["match_reason"],
                        "confidence": duplicate_check["confidence"]
                    }
                )
        
        # Auto-assign if not provided
        assigned_to_user_id = lead_data.assigned_to
        
        if not assigned_to_user_id:
            # Use assignment rules to auto-assign
            # Default: round-robin (can be configured per company)
            assigned_to_user_id = AssignmentRulesEngine.assign_lead(
                company_id=company_id,
                rule_type=AssignmentRuleType.ROUND_ROBIN,  # Can be configured
                country=lead_data.country,
                db=db
            )
            
            # Fallback to current user if no assignment possible
            if not assigned_to_user_id:
                assigned_to_user_id = current_user.id
        
        new_lead = Lead(
            company_id=company_id,
            **lead_data.model_dump(exclude={"assigned_to"}),
            created_by=current_user.id,
            assigned_to=assigned_to_user_id,
            lead_owner_id=assigned_to_user_id,  # Set lead_owner_id as well
            is_duplicate=False  # Will be set if duplicate
        )
        
        db.add(new_lead)
        db.flush()  # Flush to get ID
        
        # Calculate initial lead score
        new_lead.lead_score = LeadScoringAlgorithm.calculate_lead_score(new_lead, db)
        
        db.commit()
        db.refresh(new_lead)
        
        # Start email sequence if enabled and lead has email
        if new_lead.email:
            try:
                from app.utils.email_sequences import EmailSequenceAutomation
                # Refresh lead to ensure we have the latest data
                db.refresh(new_lead)
                EmailSequenceAutomation.start_sequence_for_lead(
                    new_lead.id, company_id, db=db
                )
            except Exception as e:
                # Log error but don't fail lead creation
                print(f"Error starting email sequence: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Log audit trail
        try:
            audit_service.log_create(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Lead",
                resource_id=new_lead.id,
                new_values={"lead_name": new_lead.lead_name, "email": new_lead.email, "company_id": company_id}
            )
            log_service.log_info(
                db=db,
                category="USER_ACTIVITY",
                action="CREATE_LEAD",
                message=f"Lead '{new_lead.lead_name}' created",
                user_id=current_user.id
            )
        except Exception:
            pass
        
        return new_lead
    
    @staticmethod
    def get_lead(
        lead_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ) -> Lead:
        """Get lead by ID"""
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        return lead
    
    @staticmethod
    def update_lead(
        lead_id: int,
        company_id: int,
        lead_data: LeadUpdate,
        current_user: User,
        db: Session
    ) -> Lead:
        """Update lead"""
        lead = LeadController.get_lead(lead_id, company_id, current_user, db)
        
        # Store old values for audit before update
        update_data = lead_data.model_dump(exclude_unset=True)
        old_values = {}
        for key in update_data.keys():
            old_values[key] = getattr(lead, key, None)
        
        # Check for duplicates if email/phone/company changed
        duplicate_check_fields = ['email', 'phone', 'company_name']
        
        if any(field in update_data for field in duplicate_check_fields):
            # Re-check for duplicates with updated data
            duplicate_check = DuplicateDetectionEngine.check_duplicate(
                company_id=company_id,
                email=update_data.get('email') or lead.email,
                phone=update_data.get('phone') or lead.phone,
                company_name=update_data.get('company_name') or lead.company_name,
                db=db,
                exclude_lead_id=lead_id
            )
            
            if duplicate_check["is_duplicate"] and not update_data.get('is_duplicate', False):
                # Warn but don't block (user might be merging)
                # Could raise exception here if strict mode
                pass
        
        for key, value in update_data.items():
            setattr(lead, key, value)
        
        # Recalculate lead score if qualification fields changed or score not explicitly set
        score_fields = ['budget_range', 'authority_level', 'timeline', 'interest_product', 'priority', 'source']
        if any(field in update_data for field in score_fields) or 'lead_score' not in update_data:
            lead.lead_score = LeadScoringAlgorithm.calculate_lead_score(lead, db)
        
        db.commit()
        db.refresh(lead)
        
        # Log audit trail for update
        try:
            audit_service.log_update(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Lead",
                resource_id=lead.id,
                old_values=old_values,
                new_values=update_data
            )
            log_service.log_info(
                db=db,
                category="USER_ACTIVITY",
                action="UPDATE_LEAD",
                message=f"Lead '{lead.lead_name}' updated",
                user_id=current_user.id
            )
        except Exception:
            pass
        
        return lead
    
    @staticmethod
    def delete_lead(
        lead_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ):
        """Delete lead"""
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
        
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        lead_name = lead.lead_name
        db.delete(lead)
        db.commit()
        
        # Log audit trail for delete
        try:
            audit_service.log_delete(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Lead",
                resource_id=lead_id,
                old_values={"lead_name": lead_name, "company_id": company_id}
            )
            log_service.log_info(
                db=db,
                category="USER_ACTIVITY",
                action="DELETE_LEAD",
                message=f"Lead '{lead_name}' deleted",
                user_id=current_user.id
            )
        except Exception:
            pass
    
    @staticmethod
    def get_lead_stats(company_id: int, db: Session) -> dict:
        """Get lead statistics for company"""
        from sqlalchemy import func
        
        total = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id
        ).scalar()
        
        by_status = {}
        statuses = ["new", "contacted", "qualified", "converted", "lost"]
        for s in statuses:
            count = db.query(func.count(Lead.id)).filter(
                Lead.company_id == company_id,
                Lead.status == s
            ).scalar()
            by_status[s] = count or 0
        
        return {
            "total_leads": total or 0,
            "by_status": by_status
        }

