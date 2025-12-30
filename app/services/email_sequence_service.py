"""
Email Sequence Automation Service
Handles automated email sequence execution, tracking, and progress management
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.email_sequence import EmailSequence
from app.models.activity import Activity


class EmailSequenceService:
    """Service for email sequence automation"""
    
    # Default score increment values
    EMAIL_OPEN_SCORE = 5
    EMAIL_CLICK_SCORE = 10
    EMAIL_REPLY_SCORE = 15
    
    @staticmethod
    def get_leads_for_sequence(
        company_id: int,
        sequence_id: int,
        db: Session
    ) -> List[Lead]:
        """
        Get leads eligible for a specific email sequence
        
        Args:
            company_id: Company ID
            sequence_id: Email sequence ID
            db: Database session
            
        Returns:
            List of eligible leads
        """
        sequence = db.query(EmailSequence).filter(
            EmailSequence.id == sequence_id,
            EmailSequence.company_id == company_id,
            EmailSequence.is_active == True
        ).first()
        
        if not sequence:
            return []
        
        # Get leads based on trigger condition
        query = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status.notin_(["converted", "disqualified"]),
            Lead.email.isnot(None)
        )
        
        # Filter by trigger condition
        if sequence.trigger_condition == "on_creation":
            # New leads created in last 24 hours
            cutoff = datetime.utcnow() - timedelta(hours=24)
            query = query.filter(Lead.created_at >= cutoff)
        elif sequence.trigger_condition == "score_threshold":
            # Leads with score >= threshold
            threshold = sequence.score_threshold or 50
            query = query.filter(Lead.lead_score >= threshold)
        
        return query.all()
    
    @staticmethod
    def start_sequence_for_lead(
        lead_id: int,
        sequence_id: int,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Start an email sequence for a lead
        
        Args:
            lead_id: Lead ID
            sequence_id: Email sequence ID
            company_id: Company ID
            db: Database session
            
        Returns:
            Sequence start result
        """
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            return {"success": False, "error": "Lead not found"}
        
        sequence = db.query(EmailSequence).filter(
            EmailSequence.id == sequence_id,
            EmailSequence.company_id == company_id
        ).first()
        
        if not sequence:
            return {"success": False, "error": "Sequence not found"}
        
        # Log sequence start as activity
        activity = Activity(
            company_id=company_id,
            lead_id=lead_id,
            activity_type="email",
            title=f"Email Sequence Started: {sequence.name}",
            description=f"Lead enrolled in email sequence '{sequence.name}'",
            user_id=lead.assigned_to or lead.created_by,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "lead_id": lead_id,
            "sequence_id": sequence_id,
            "sequence_name": sequence.name,
            "started_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def track_email_event(
        lead_id: int,
        company_id: int,
        event_type: str,
        email_id: Optional[str],
        db: Session
    ) -> Dict:
        """
        Track email engagement event and update lead score
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            event_type: Event type (open, click, reply, bounce, unsubscribe)
            email_id: Email identifier
            db: Database session
            
        Returns:
            Tracking result with score update
        """
        from app.utils.lead_scoring import LeadScoringAlgorithm
        
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            return {"success": False, "error": "Lead not found"}
        
        # Determine score increment based on event type
        score_increment = 0
        event_description = ""
        
        if event_type == "open":
            score_increment = EmailSequenceService.EMAIL_OPEN_SCORE
            event_description = "Email opened"
        elif event_type == "click":
            score_increment = EmailSequenceService.EMAIL_CLICK_SCORE
            event_description = "Email link clicked"
        elif event_type == "reply":
            score_increment = EmailSequenceService.EMAIL_REPLY_SCORE
            event_description = "Email replied"
        elif event_type == "bounce":
            score_increment = -5
            event_description = "Email bounced"
        elif event_type == "unsubscribe":
            score_increment = -10
            event_description = "Unsubscribed from emails"
        
        # Update lead score
        new_score = None
        if score_increment != 0:
            new_score = LeadScoringAlgorithm.increment_lead_score(
                lead_id=lead_id,
                company_id=company_id,
                increment=score_increment,
                db=db,
                reason=event_description
            )
        
        # Log activity
        activity = Activity(
            company_id=company_id,
            lead_id=lead_id,
            activity_type="email",
            title=f"Email Event: {event_type.title()}",
            description=f"{event_description}. Score change: {score_increment:+d}",
            outcome="positive" if score_increment > 0 else "negative" if score_increment < 0 else "neutral",
            user_id=lead.assigned_to or lead.created_by,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "lead_id": lead_id,
            "event_type": event_type,
            "score_increment": score_increment,
            "new_score": new_score,
            "tracked_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_sequence_analytics(
        company_id: int,
        sequence_id: Optional[int],
        db: Session
    ) -> Dict:
        """
        Get email sequence analytics
        
        Args:
            company_id: Company ID
            sequence_id: Optional sequence ID (None for all sequences)
            db: Database session
            
        Returns:
            Sequence analytics
        """
        from sqlalchemy import func
        
        # Get sequences
        query = db.query(EmailSequence).filter(EmailSequence.company_id == company_id)
        if sequence_id:
            query = query.filter(EmailSequence.id == sequence_id)
        
        sequences = query.all()
        
        # Get email activities
        email_activities = db.query(Activity).filter(
            Activity.company_id == company_id,
            Activity.activity_type == "email"
        ).all()
        
        # Calculate metrics
        total_sent = len([a for a in email_activities if "sent" in (a.title or "").lower()])
        total_opens = len([a for a in email_activities if "open" in (a.title or "").lower()])
        total_clicks = len([a for a in email_activities if "click" in (a.title or "").lower()])
        total_replies = len([a for a in email_activities if "reply" in (a.title or "").lower()])
        
        return {
            "total_sequences": len(sequences),
            "active_sequences": len([s for s in sequences if s.is_active]),
            "email_metrics": {
                "total_sent": total_sent,
                "total_opens": total_opens,
                "total_clicks": total_clicks,
                "total_replies": total_replies,
                "open_rate": round((total_opens / total_sent * 100), 2) if total_sent > 0 else 0,
                "click_rate": round((total_clicks / total_sent * 100), 2) if total_sent > 0 else 0,
                "reply_rate": round((total_replies / total_sent * 100), 2) if total_sent > 0 else 0
            },
            "sequences": [
                {
                    "id": s.id,
                    "name": s.name,
                    "is_active": s.is_active,
                    "trigger_condition": s.trigger_condition,
                    "total_emails": s.total_emails
                }
                for s in sequences
            ]
        }
    
    @staticmethod
    def get_pending_emails(company_id: int, db: Session) -> List[Dict]:
        """
        Get pending emails to be sent
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            List of pending emails
        """
        # Get active sequences
        sequences = db.query(EmailSequence).filter(
            EmailSequence.company_id == company_id,
            EmailSequence.is_active == True
        ).all()
        
        pending = []
        for sequence in sequences:
            leads = EmailSequenceService.get_leads_for_sequence(company_id, sequence.id, db)
            for lead in leads:
                if lead.email:
                    pending.append({
                        "lead_id": lead.id,
                        "lead_name": lead.lead_name,
                        "email": lead.email,
                        "sequence_id": sequence.id,
                        "sequence_name": sequence.name
                    })
        
        return pending
