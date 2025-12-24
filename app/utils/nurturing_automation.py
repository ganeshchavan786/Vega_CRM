"""
Lead Nurturing Automation
Auto-creates tasks for SDRs and manages conversion triggers
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from app.models.lead import Lead
from app.models.task import Task
from app.models.user import User


class NurturingAutomation:
    """Automated nurturing tasks and conversion triggers"""
    
    # Configuration
    AUTO_TASK_DAYS_THRESHOLD = 7  # Create task after 7 days
    CONVERSION_SCORE_THRESHOLD = 70  # Minimum score for conversion
    CONVERSION_STATUS_REQUIRED = "contacted"  # Required status for conversion
    
    @staticmethod
    def check_and_create_followup_task(
        lead_id: int,
        company_id: int,
        db: Session
    ) -> Optional[Task]:
        """
        Check if lead needs follow-up task and create it
        
        Rules:
        - Create task if lead is 7+ days old
        - Only for active leads (not converted/disqualified)
        - Assign to lead owner (SDR)
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            
        Returns:
            Created task or None
        """
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            return None
        
        # Skip if lead is converted or disqualified
        if lead.status in ["converted", "disqualified"]:
            return None
        
        # Skip if no assigned owner
        if not lead.assigned_to:
            return None
        
        # Check if lead is 7+ days old
        if lead.created_at:
            days_old = (datetime.utcnow() - lead.created_at).days
            if days_old < NurturingAutomation.AUTO_TASK_DAYS_THRESHOLD:
                return None  # Too new, no task needed
        
        # Check if task already exists for this lead
        existing_task = db.query(Task).filter(
            and_(
                Task.company_id == company_id,
                Task.lead_id == lead_id,
                Task.task_type == "follow_up",
                Task.status.in_(["pending", "in_progress"])
            )
        ).first()
        
        if existing_task:
            return None  # Task already exists
        
        # Create follow-up task
        due_date = datetime.utcnow() + timedelta(days=1)  # Due tomorrow
        
        new_task = Task(
            company_id=company_id,
            title=f"Follow-up with {lead.full_name}",
            description=f"Auto-generated follow-up task for lead: {lead.full_name} ({lead.company_name or 'N/A'}). Lead created {days_old} days ago.",
            task_type="follow_up",
            priority="medium",
            status="pending",
            due_date=due_date,
            lead_id=lead_id,
            assigned_to=lead.assigned_to,
            created_by=lead.assigned_to  # System-created, but assigned to SDR
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        return new_task
    
    @staticmethod
    def check_conversion_eligibility(
        lead_id: int,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Check if lead is eligible for conversion
        
        Conversion Trigger:
        IF Lead Score > 70 AND Lead Status = "Contacted"
        THEN Allow Conversion
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            
        Returns:
            Dictionary with eligibility information
        """
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            return {
                "eligible": False,
                "reason": "Lead not found"
            }
        
        # Check if already converted
        if lead.status == "converted":
            return {
                "eligible": False,
                "reason": "Lead already converted"
            }
        
        # Check score threshold
        score_met = (lead.lead_score or 0) >= NurturingAutomation.CONVERSION_SCORE_THRESHOLD
        
        # Check status requirement
        status_met = lead.status.lower() == NurturingAutomation.CONVERSION_STATUS_REQUIRED.lower()
        
        eligible = score_met and status_met
        
        reasons = []
        if not score_met:
            reasons.append(f"Lead score ({lead.lead_score or 0}) is below threshold ({NurturingAutomation.CONVERSION_SCORE_THRESHOLD})")
        if not status_met:
            reasons.append(f"Lead status ({lead.status}) is not '{NurturingAutomation.CONVERSION_STATUS_REQUIRED}'")
        
        return {
            "eligible": eligible,
            "reason": "; ".join(reasons) if reasons else "Lead is eligible for conversion",
            "lead_score": lead.lead_score or 0,
            "lead_status": lead.status,
            "score_threshold": NurturingAutomation.CONVERSION_SCORE_THRESHOLD,
            "required_status": NurturingAutomation.CONVERSION_STATUS_REQUIRED,
            "score_met": score_met,
            "status_met": status_met
        }
    
    @staticmethod
    def process_nurturing_tasks(
        company_id: int,
        db: Session,
        dry_run: bool = False
    ) -> Dict:
        """
        Process all leads and create follow-up tasks where needed
        
        Args:
            company_id: Company ID
            db: Database session
            dry_run: If True, don't create tasks, just return plan
            
        Returns:
            Dictionary with processing results
        """
        # Get all active leads that are 7+ days old
        seven_days_ago = datetime.utcnow() - timedelta(days=NurturingAutomation.AUTO_TASK_DAYS_THRESHOLD)
        
        leads = db.query(Lead).filter(
            and_(
                Lead.company_id == company_id,
                Lead.status.notin_(["converted", "disqualified"]),
                Lead.created_at <= seven_days_ago,
                Lead.assigned_to.isnot(None)
            )
        ).all()
        
        tasks_created = 0
        tasks_skipped = 0
        task_plan = []
        
        for lead in leads:
            # Check if task already exists
            existing_task = db.query(Task).filter(
                and_(
                    Task.company_id == company_id,
                    Task.lead_id == lead.id,
                    Task.task_type == "follow_up",
                    Task.status.in_(["pending", "in_progress"])
                )
            ).first()
            
            if existing_task:
                tasks_skipped += 1
                continue
            
            days_old = (datetime.utcnow() - lead.created_at).days
            
            task_info = {
                "lead_id": lead.id,
                "lead_name": lead.full_name,
                "lead_company": lead.company_name,
                "days_old": days_old,
                "assigned_to": lead.assigned_to,
                "lead_score": lead.lead_score or 0
            }
            
            if not dry_run:
                # Create task
                due_date = datetime.utcnow() + timedelta(days=1)
                
                new_task = Task(
                    company_id=company_id,
                    title=f"Follow-up with {lead.full_name}",
                    description=f"Auto-generated follow-up task for lead: {lead.full_name} ({lead.company_name or 'N/A'}). Lead created {days_old} days ago.",
                    task_type="follow_up",
                    priority="medium",
                    status="pending",
                    due_date=due_date,
                    lead_id=lead.id,
                    assigned_to=lead.assigned_to,
                    created_by=lead.assigned_to
                )
                
                db.add(new_task)
                tasks_created += 1
            else:
                task_plan.append(task_info)
        
        if not dry_run:
            db.commit()
        
        return {
            "leads_processed": len(leads),
            "tasks_created": tasks_created,
            "tasks_skipped": tasks_skipped,
            "task_plan": task_plan if dry_run else [],
            "dry_run": dry_run
        }
    
    @staticmethod
    def get_nurturing_stats(
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Get nurturing statistics for company
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Dictionary with nurturing statistics
        """
        # Count leads by status
        total_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id
        ).scalar() or 0
        
        active_leads = db.query(func.count(Lead.id)).filter(
            and_(
                Lead.company_id == company_id,
                Lead.status.notin_(["converted", "disqualified"])
            )
        ).scalar() or 0
        
        # Count leads eligible for conversion
        conversion_eligible = db.query(func.count(Lead.id)).filter(
            and_(
                Lead.company_id == company_id,
                Lead.status == "contacted",
                Lead.lead_score >= NurturingAutomation.CONVERSION_SCORE_THRESHOLD
            )
        ).scalar() or 0
        
        # Count leads needing follow-up (7+ days old, no task)
        seven_days_ago = datetime.utcnow() - timedelta(days=NurturingAutomation.AUTO_TASK_DAYS_THRESHOLD)
        
        leads_needing_followup = db.query(Lead).filter(
            and_(
                Lead.company_id == company_id,
                Lead.status.notin_(["converted", "disqualified"]),
                Lead.created_at <= seven_days_ago,
                Lead.assigned_to.isnot(None)
            )
        ).all()
        
        followup_count = 0
        for lead in leads_needing_followup:
            existing_task = db.query(Task).filter(
                and_(
                    Task.company_id == company_id,
                    Task.lead_id == lead.id,
                    Task.task_type == "follow_up",
                    Task.status.in_(["pending", "in_progress"])
                )
            ).first()
            
            if not existing_task:
                followup_count += 1
        
        # Count pending follow-up tasks
        pending_followup_tasks = db.query(func.count(Task.id)).filter(
            and_(
                Task.company_id == company_id,
                Task.task_type == "follow_up",
                Task.status == "pending"
            )
        ).scalar() or 0
        
        return {
            "total_leads": total_leads,
            "active_leads": active_leads,
            "conversion_eligible": conversion_eligible,
            "leads_needing_followup": followup_count,
            "pending_followup_tasks": pending_followup_tasks,
            "conversion_threshold": NurturingAutomation.CONVERSION_SCORE_THRESHOLD,
            "task_threshold_days": NurturingAutomation.AUTO_TASK_DAYS_THRESHOLD
        }

