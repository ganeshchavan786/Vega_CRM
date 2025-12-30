"""
Task Automation Service
Handles automatic task creation, assignment, reminders, and escalation
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.task import Task
from app.models.activity import Activity


class TaskAutomationService:
    """Service for task automation"""
    
    # Default task creation rules
    DEFAULT_FOLLOW_UP_DAYS = 7  # Create follow-up task after 7 days
    DEFAULT_ESCALATION_DAYS = 3  # Escalate if overdue by 3 days
    
    @staticmethod
    def create_follow_up_task(
        lead_id: int,
        company_id: int,
        user_id: int,
        db: Session,
        days_delay: int = 7,
        task_type: str = "follow_up",
        priority: str = "medium"
    ) -> Dict:
        """
        Create automatic follow-up task for a lead
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            user_id: User ID to assign task
            db: Database session
            days_delay: Days from now for due date
            task_type: Task type
            priority: Task priority
            
        Returns:
            Created task details
        """
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            return {"success": False, "error": "Lead not found"}
        
        # Create task
        due_date = datetime.utcnow() + timedelta(days=days_delay)
        
        task = Task(
            company_id=company_id,
            title=f"Follow up with {lead.lead_name}",
            description=f"Automatic follow-up task for lead: {lead.lead_name}. Email: {lead.email}, Phone: {lead.phone}",
            task_type=task_type,
            priority=priority,
            status="pending",
            due_date=due_date,
            assigned_to=user_id or lead.assigned_to or lead.lead_owner_id,
            lead_id=lead_id,
            created_by=user_id
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Log activity
        activity = Activity(
            company_id=company_id,
            lead_id=lead_id,
            activity_type="task",
            title=f"Auto Task Created: {task.title}",
            description=f"Automatic follow-up task created. Due: {due_date.strftime('%Y-%m-%d')}",
            user_id=user_id,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "due_date": due_date.isoformat(),
            "assigned_to": task.assigned_to
        }
    
    @staticmethod
    def create_task_on_score_change(
        lead_id: int,
        company_id: int,
        old_score: int,
        new_score: int,
        db: Session
    ) -> Optional[Dict]:
        """
        Create task when lead score crosses threshold
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            old_score: Previous score
            new_score: New score
            db: Database session
            
        Returns:
            Created task details or None
        """
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            return None
        
        # Check if score crossed high threshold (70)
        if old_score < 70 and new_score >= 70:
            task = Task(
                company_id=company_id,
                title=f"Hot Lead: {lead.lead_name} - Score {new_score}",
                description=f"Lead score crossed 70 threshold. Previous: {old_score}, Current: {new_score}. Contact immediately!",
                task_type="call",
                priority="high",
                status="pending",
                due_date=datetime.utcnow() + timedelta(hours=24),
                assigned_to=lead.assigned_to or lead.lead_owner_id,
                lead_id=lead_id,
                created_by=lead.assigned_to or lead.created_by
            )
            
            db.add(task)
            db.commit()
            db.refresh(task)
            
            return {
                "success": True,
                "task_id": task.id,
                "reason": "score_threshold_crossed",
                "threshold": 70
            }
        
        # Check if score crossed medium threshold (40)
        elif old_score < 40 and new_score >= 40:
            task = Task(
                company_id=company_id,
                title=f"Warm Lead: {lead.lead_name} - Score {new_score}",
                description=f"Lead score crossed 40 threshold. Previous: {old_score}, Current: {new_score}. Schedule follow-up.",
                task_type="follow_up",
                priority="medium",
                status="pending",
                due_date=datetime.utcnow() + timedelta(days=2),
                assigned_to=lead.assigned_to or lead.lead_owner_id,
                lead_id=lead_id,
                created_by=lead.assigned_to or lead.created_by
            )
            
            db.add(task)
            db.commit()
            db.refresh(task)
            
            return {
                "success": True,
                "task_id": task.id,
                "reason": "score_threshold_crossed",
                "threshold": 40
            }
        
        return None
    
    @staticmethod
    def get_overdue_tasks(company_id: int, db: Session) -> List[Dict]:
        """
        Get overdue tasks for escalation
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            List of overdue tasks
        """
        now = datetime.utcnow()
        
        overdue_tasks = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date < now
        ).all()
        
        return [
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "days_overdue": (now - t.due_date).days if t.due_date else 0,
                "assigned_to": t.assigned_to,
                "priority": t.priority,
                "lead_id": t.lead_id,
                "customer_id": t.customer_id
            }
            for t in overdue_tasks
        ]
    
    @staticmethod
    def escalate_overdue_tasks(
        company_id: int,
        db: Session,
        escalation_days: int = 3
    ) -> Dict:
        """
        Escalate tasks overdue by specified days
        
        Args:
            company_id: Company ID
            db: Database session
            escalation_days: Days overdue to trigger escalation
            
        Returns:
            Escalation results
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(days=escalation_days)
        
        # Find tasks overdue by escalation_days
        tasks_to_escalate = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date < cutoff,
            Task.priority != "urgent"  # Don't escalate already urgent tasks
        ).all()
        
        escalated = 0
        for task in tasks_to_escalate:
            old_priority = task.priority
            task.priority = "urgent" if old_priority == "high" else "high"
            
            # Log escalation
            activity = Activity(
                company_id=company_id,
                lead_id=task.lead_id,
                customer_id=task.customer_id,
                deal_id=task.deal_id,
                activity_type="task",
                title=f"Task Escalated: {task.title}",
                description=f"Task escalated from {old_priority} to {task.priority} due to being overdue",
                user_id=task.assigned_to,
                activity_date=datetime.utcnow()
            )
            db.add(activity)
            escalated += 1
        
        db.commit()
        
        return {
            "total_overdue": len(tasks_to_escalate),
            "escalated": escalated,
            "escalation_threshold_days": escalation_days
        }
    
    @staticmethod
    def auto_create_tasks_for_new_leads(
        company_id: int,
        db: Session,
        days_since_creation: int = 7
    ) -> Dict:
        """
        Auto-create follow-up tasks for leads without recent tasks
        
        Args:
            company_id: Company ID
            db: Database session
            days_since_creation: Days after lead creation to create task
            
        Returns:
            Task creation results
        """
        cutoff = datetime.utcnow() - timedelta(days=days_since_creation)
        
        # Find leads created before cutoff without pending tasks
        leads_without_tasks = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status.notin_(["converted", "disqualified"]),
            Lead.created_at <= cutoff
        ).all()
        
        created = 0
        for lead in leads_without_tasks:
            # Check if lead has pending task
            existing_task = db.query(Task).filter(
                Task.lead_id == lead.id,
                Task.status.in_(["pending", "in_progress"])
            ).first()
            
            if not existing_task:
                task = Task(
                    company_id=company_id,
                    title=f"Follow up: {lead.lead_name} (Auto-created)",
                    description=f"Auto-created task for lead without recent activity. Lead created: {lead.created_at.strftime('%Y-%m-%d')}",
                    task_type="follow_up",
                    priority="medium",
                    status="pending",
                    due_date=datetime.utcnow() + timedelta(days=2),
                    assigned_to=lead.assigned_to or lead.lead_owner_id,
                    lead_id=lead.id,
                    created_by=lead.assigned_to or lead.created_by
                )
                db.add(task)
                created += 1
        
        db.commit()
        
        return {
            "leads_checked": len(leads_without_tasks),
            "tasks_created": created
        }
    
    @staticmethod
    def get_task_automation_stats(company_id: int, db: Session) -> Dict:
        """
        Get task automation statistics
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Task automation stats
        """
        from sqlalchemy import func
        
        now = datetime.utcnow()
        
        # Total tasks
        total_tasks = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id
        ).scalar() or 0
        
        # Pending tasks
        pending_tasks = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id,
            Task.status == "pending"
        ).scalar() or 0
        
        # Overdue tasks
        overdue_tasks = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id,
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date < now
        ).scalar() or 0
        
        # Completed today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id,
            Task.status == "completed",
            Task.updated_at >= today_start
        ).scalar() or 0
        
        # Tasks by priority
        by_priority = {}
        for priority in ["low", "medium", "high", "urgent"]:
            count = db.query(func.count(Task.id)).filter(
                Task.company_id == company_id,
                Task.priority == priority,
                Task.status.in_(["pending", "in_progress"])
            ).scalar() or 0
            by_priority[priority] = count
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "overdue_tasks": overdue_tasks,
            "completed_today": completed_today,
            "by_priority": by_priority,
            "overdue_rate": round((overdue_tasks / pending_tasks * 100), 2) if pending_tasks > 0 else 0
        }
