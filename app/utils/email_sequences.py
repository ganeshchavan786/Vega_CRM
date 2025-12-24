"""
Email Sequence Automation
Manages drip campaign email sequences for lead nurturing
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from app.models.lead import Lead
from app.models.email_sequence import EmailSequence, EmailSequenceEmail
from app.models.activity import Activity


class EmailSequenceAutomation:
    """Email sequence automation for lead nurturing"""
    
    # Default sequence configuration
    DEFAULT_SEQUENCE_DAYS = [0, 3, 7, 10, 14]  # Days after lead creation
    DEFAULT_SUBJECTS = [
        "Welcome to {company_name}!",
        "Learn more about our solutions",
        "How we can help your business",
        "Success stories from customers like you",
        "Let's schedule a conversation"
    ]
    DEFAULT_BODY_TEMPLATES = [
        "Welcome {first_name}! Thank you for your interest in {company_name}.",
        "Hi {first_name}, I wanted to share how our solutions can help {company_name}.",
        "Hello {first_name}, here's how we've helped similar businesses...",
        "{first_name}, here are some success stories from our customers.",
        "Hi {first_name}, let's schedule a time to discuss how we can help."
    ]
    
    @staticmethod
    def get_default_sequence(company_id: int, db: Session) -> Optional[EmailSequence]:
        """
        Get or create default email sequence for company
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Email sequence or None
        """
        # Check if default sequence exists
        sequence = db.query(EmailSequence).filter(
            and_(
                EmailSequence.company_id == company_id,
                EmailSequence.name == "Default Nurturing Sequence",
                EmailSequence.is_active == True
            )
        ).first()
        
        if sequence:
            return sequence
        
        # Create default sequence
        email_templates = []
        for i, (day, subject, body) in enumerate(zip(
            EmailSequenceAutomation.DEFAULT_SEQUENCE_DAYS,
            EmailSequenceAutomation.DEFAULT_SUBJECTS,
            EmailSequenceAutomation.DEFAULT_BODY_TEMPLATES
        ), 1):
            email_templates.append({
                "email_number": i,
                "delay_days": day,
                "subject": subject,
                "body": body
            })
        
        sequence = EmailSequence(
            company_id=company_id,
            name="Default Nurturing Sequence",
            description="Default 5-email nurturing sequence over 14 days",
            is_active=True,
            trigger_on_creation=True,
            trigger_score_threshold=None,
            total_emails=5,
            sequence_duration_days=14,
            email_templates=email_templates
        )
        
        db.add(sequence)
        db.commit()
        db.refresh(sequence)
        
        return sequence
    
    @staticmethod
    def start_sequence_for_lead(
        lead_id: int,
        company_id: int,
        sequence_id: Optional[int] = None,
        db: Session = None
    ) -> Dict:
        """
        Start email sequence for a lead
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            sequence_id: Sequence ID (uses default if None)
            db: Database session
            
        Returns:
            Dictionary with sequence start results
        """
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            raise ValueError("Lead not found")
        
        # Check if sequence already started
        existing = db.query(EmailSequenceEmail).filter(
            and_(
                EmailSequenceEmail.lead_id == lead_id,
                EmailSequenceEmail.status != "failed"
            )
        ).first()
        
        if existing:
            return {
                "success": False,
                "message": "Email sequence already started for this lead",
                "sequence_email_id": existing.id
            }
        
        # Get sequence
        if sequence_id:
            sequence = db.query(EmailSequence).filter(
                and_(
                    EmailSequence.id == sequence_id,
                    EmailSequence.company_id == company_id,
                    EmailSequence.is_active == True
                )
            ).first()
        else:
            sequence = EmailSequenceAutomation.get_default_sequence(company_id, db)
        
        if not sequence:
            raise ValueError("Email sequence not found")
        
        # Check if lead has email
        if not lead.email:
            return {
                "success": False,
                "message": "Lead does not have email address"
            }
        
        # Create email sequence emails
        created_emails = []
        lead_created_at = lead.created_at or datetime.utcnow()
        
        templates = sequence.email_templates or []
        if not templates:
            # Use default templates
            templates = []
            for i, (day, subject, body) in enumerate(zip(
                EmailSequenceAutomation.DEFAULT_SEQUENCE_DAYS,
                EmailSequenceAutomation.DEFAULT_SUBJECTS,
                EmailSequenceAutomation.DEFAULT_BODY_TEMPLATES
            ), 1):
                templates.append({
                    "email_number": i,
                    "delay_days": day,
                    "subject": subject,
                    "body": body
                })
        
        for template in templates:
            email_number = template.get("email_number", 1)
            delay_days = template.get("delay_days", 0)
            subject_template = template.get("subject", "Follow-up")
            body_template = template.get("body", "")
            
            # Replace placeholders
            first_name = lead.first_name or "there"
            company_name = lead.company_name or "our company"
            
            subject = subject_template.replace("{first_name}", first_name).replace("{company_name}", company_name)
            body = body_template.replace("{first_name}", first_name).replace("{company_name}", company_name)
            
            # Calculate scheduled send date
            scheduled_send_date = lead_created_at + timedelta(days=delay_days)
            
            # Skip if scheduled date is in the past (for existing leads)
            if scheduled_send_date < datetime.utcnow():
                scheduled_send_date = datetime.utcnow() + timedelta(days=1)  # Send tomorrow
            
            sequence_email = EmailSequenceEmail(
                sequence_id=sequence.id,
                lead_id=lead_id,
                email_number=email_number,
                subject=subject,
                body_text=body,
                delay_days=delay_days,
                scheduled_send_date=scheduled_send_date,
                status="pending"
            )
            
            db.add(sequence_email)
            created_emails.append(sequence_email)
        
        db.commit()
        
        # Log activity - use lead owner or created_by, fallback to system user (ID 1)
        activity_user_id = lead.lead_owner_id
        if not activity_user_id and hasattr(lead, 'created_by') and lead.created_by:
            activity_user_id = lead.created_by
        if not activity_user_id:
            # Fallback to admin/system user (ID 1)
            activity_user_id = 1
        
        activity = Activity(
            company_id=company_id,
            lead_id=lead_id,
            activity_type="note",
            title="Email Sequence Started",
            description=f"Email nurturing sequence started for lead. {len(created_emails)} emails scheduled.",
            user_id=activity_user_id,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "message": f"Email sequence started: {len(created_emails)} emails scheduled",
            "sequence_id": sequence.id,
            "sequence_name": sequence.name,
            "emails_created": len(created_emails),
            "first_email_date": created_emails[0].scheduled_send_date.isoformat() if created_emails else None
        }
    
    @staticmethod
    def track_email_open(
        sequence_email_id: int,
        db: Session
    ) -> bool:
        """
        Track email open event (+5 points to lead score)
        
        Args:
            sequence_email_id: Email sequence email ID
            db: Database session
            
        Returns:
            True if tracked successfully
        """
        sequence_email = db.query(EmailSequenceEmail).filter(
            EmailSequenceEmail.id == sequence_email_id
        ).first()
        
        if not sequence_email:
            return False
        
        # Update open tracking
        if not sequence_email.opened_at:
            sequence_email.opened_at = datetime.utcnow()
            sequence_email.status = "opened"
        
        sequence_email.open_count += 1
        db.commit()
        
        # Increment lead score (+5 points)
        lead = db.query(Lead).filter(Lead.id == sequence_email.lead_id).first()
        if lead:
            from app.utils.lead_scoring import LeadScoringAlgorithm
            # Increment score by 5
            current_score = lead.lead_score or 0
            lead.lead_score = min(100, current_score + 5)  # Cap at 100
            db.commit()
        
        return True
    
    @staticmethod
    def track_email_click(
        sequence_email_id: int,
        db: Session
    ) -> bool:
        """
        Track email click event (+10 points to lead score)
        
        Args:
            sequence_email_id: Email sequence email ID
            db: Database session
            
        Returns:
            True if tracked successfully
        """
        sequence_email = db.query(EmailSequenceEmail).filter(
            EmailSequenceEmail.id == sequence_email_id
        ).first()
        
        if not sequence_email:
            return False
        
        # Update click tracking
        if not sequence_email.clicked_at:
            sequence_email.clicked_at = datetime.utcnow()
            sequence_email.status = "clicked"
        
        sequence_email.click_count += 1
        db.commit()
        
        # Increment lead score (+10 points)
        lead = db.query(Lead).filter(Lead.id == sequence_email.lead_id).first()
        if lead:
            current_score = lead.lead_score or 0
            lead.lead_score = min(100, current_score + 10)  # Cap at 100
            db.commit()
        
        return True
    
    @staticmethod
    def get_pending_emails(
        company_id: int,
        db: Session,
        limit: int = 100
    ) -> List[EmailSequenceEmail]:
        """
        Get pending emails ready to send
        
        Args:
            company_id: Company ID
            db: Database session
            limit: Maximum number of emails to return
            
        Returns:
            List of pending emails
        """
        now = datetime.utcnow()
        
        pending = db.query(EmailSequenceEmail).join(Lead).filter(
            and_(
                Lead.company_id == company_id,
                EmailSequenceEmail.status == "pending",
                EmailSequenceEmail.scheduled_send_date <= now
            )
        ).limit(limit).all()
        
        return pending
    
    @staticmethod
    def get_sequence_status(
        lead_id: int,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Get email sequence status for lead
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            
        Returns:
            Dictionary with sequence status
        """
        emails = db.query(EmailSequenceEmail).filter(
            EmailSequenceEmail.lead_id == lead_id
        ).order_by(EmailSequenceEmail.email_number).all()
        
        if not emails:
            return {
                "sequence_started": False,
                "total_emails": 0,
                "sent": 0,
                "opened": 0,
                "clicked": 0,
                "pending": 0
            }
        
        sent = sum(1 for e in emails if e.status == "sent")
        opened = sum(1 for e in emails if e.status == "opened")
        clicked = sum(1 for e in emails if e.status == "clicked")
        pending = sum(1 for e in emails if e.status == "pending")
        
        return {
            "sequence_started": True,
            "sequence_id": emails[0].sequence_id if emails else None,
            "total_emails": len(emails),
            "sent": sent,
            "opened": opened,
            "clicked": clicked,
            "pending": pending,
            "emails": [e.to_dict() for e in emails]
        }

