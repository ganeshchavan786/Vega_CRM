"""
WhatsApp Integration Service
Handles WhatsApp Business API integration, messaging, and tracking
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.activity import Activity


class WhatsAppService:
    """Service for WhatsApp Business API integration"""
    
    # Message status values
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_READ = "read"
    STATUS_FAILED = "failed"
    
    # Default templates
    DEFAULT_TEMPLATES = {
        "welcome": {
            "name": "welcome_message",
            "content": "Hello {{name}}, thank you for your interest in our services. How can we help you today?"
        },
        "follow_up": {
            "name": "follow_up_message",
            "content": "Hi {{name}}, we wanted to follow up on your inquiry. Are you available for a quick call?"
        },
        "reminder": {
            "name": "appointment_reminder",
            "content": "Hi {{name}}, this is a reminder about your scheduled appointment. Please confirm your availability."
        }
    }
    
    @staticmethod
    def send_message(
        phone: str,
        message: str,
        lead_id: Optional[int],
        company_id: int,
        user_id: int,
        db: Session,
        template_name: Optional[str] = None
    ) -> Dict:
        """
        Send WhatsApp message
        
        Args:
            phone: Recipient phone number
            message: Message content
            lead_id: Optional lead ID
            company_id: Company ID
            user_id: User ID sending message
            db: Database session
            template_name: Optional template name
            
        Returns:
            Send result
        """
        # Validate phone number
        if not phone:
            return {"success": False, "error": "Phone number required"}
        
        # Format phone number (ensure it has country code)
        formatted_phone = WhatsAppService._format_phone(phone)
        
        # In production, this would call WhatsApp Business API
        # For now, we simulate the send and log it
        
        message_id = f"wa_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{lead_id or 'unknown'}"
        
        # Log activity
        activity = Activity(
            company_id=company_id,
            lead_id=lead_id,
            activity_type="whatsapp",
            title=f"WhatsApp Message Sent",
            description=f"Message sent to {formatted_phone}: {message[:100]}...",
            outcome="positive",
            user_id=user_id,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "message_id": message_id,
            "phone": formatted_phone,
            "status": WhatsAppService.STATUS_SENT,
            "sent_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def send_template_message(
        phone: str,
        template_name: str,
        lead_id: Optional[int],
        company_id: int,
        user_id: int,
        db: Session,
        variables: Optional[Dict] = None
    ) -> Dict:
        """
        Send WhatsApp template message
        
        Args:
            phone: Recipient phone number
            template_name: Template name
            lead_id: Optional lead ID
            company_id: Company ID
            user_id: User ID sending message
            db: Database session
            variables: Template variables
            
        Returns:
            Send result
        """
        template = WhatsAppService.DEFAULT_TEMPLATES.get(template_name)
        if not template:
            return {"success": False, "error": f"Template '{template_name}' not found"}
        
        # Replace variables in template
        message = template["content"]
        if variables:
            for key, value in variables.items():
                message = message.replace(f"{{{{{key}}}}}", str(value))
        
        return WhatsAppService.send_message(
            phone=phone,
            message=message,
            lead_id=lead_id,
            company_id=company_id,
            user_id=user_id,
            db=db,
            template_name=template_name
        )
    
    @staticmethod
    def _format_phone(phone: str) -> str:
        """Format phone number for WhatsApp"""
        # Remove non-digits
        digits = "".join(filter(str.isdigit, phone))
        
        # Add country code if missing (default to India +91)
        if len(digits) == 10:
            digits = "91" + digits
        elif not digits.startswith("91") and len(digits) == 10:
            digits = "91" + digits
        
        return digits
    
    @staticmethod
    def handle_incoming_message(
        phone: str,
        message: str,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Handle incoming WhatsApp message (webhook)
        
        Args:
            phone: Sender phone number
            message: Message content
            company_id: Company ID
            db: Database session
            
        Returns:
            Processing result
        """
        # Find lead by phone
        formatted_phone = WhatsAppService._format_phone(phone)
        
        lead = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.phone.contains(formatted_phone[-10:])  # Match last 10 digits
        ).first()
        
        # Log activity
        activity = Activity(
            company_id=company_id,
            lead_id=lead.id if lead else None,
            activity_type="whatsapp",
            title="WhatsApp Message Received",
            description=f"Message from {phone}: {message[:200]}",
            outcome="positive",
            user_id=lead.assigned_to if lead else None,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        
        # Increment lead score if lead found
        if lead:
            from app.utils.lead_scoring import LeadScoringAlgorithm
            LeadScoringAlgorithm.increment_lead_score(
                lead_id=lead.id,
                company_id=company_id,
                increment=10,
                db=db,
                reason="WhatsApp message received"
            )
        
        db.commit()
        
        return {
            "success": True,
            "lead_found": lead is not None,
            "lead_id": lead.id if lead else None,
            "processed_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def update_message_status(
        message_id: str,
        status: str,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Update message delivery status (webhook)
        
        Args:
            message_id: WhatsApp message ID
            status: New status (delivered, read, failed)
            company_id: Company ID
            db: Database session
            
        Returns:
            Update result
        """
        valid_statuses = [
            WhatsAppService.STATUS_DELIVERED,
            WhatsAppService.STATUS_READ,
            WhatsAppService.STATUS_FAILED
        ]
        
        if status not in valid_statuses:
            return {"success": False, "error": f"Invalid status: {status}"}
        
        # In production, this would update message record
        # For now, just log it
        
        return {
            "success": True,
            "message_id": message_id,
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_opt_in_status(phone: str, company_id: int, db: Session) -> Dict:
        """
        Check WhatsApp opt-in status for a phone number
        
        Args:
            phone: Phone number
            company_id: Company ID
            db: Database session
            
        Returns:
            Opt-in status
        """
        # In production, this would check opt-in database
        # For now, assume opted in if lead exists with phone consent
        
        formatted_phone = WhatsAppService._format_phone(phone)
        
        lead = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.phone.contains(formatted_phone[-10:])
        ).first()
        
        return {
            "phone": formatted_phone,
            "opted_in": True,  # Default to true for existing leads
            "lead_id": lead.id if lead else None,
            "can_send": True
        }
    
    @staticmethod
    def schedule_follow_up_messages(
        lead_id: int,
        company_id: int,
        db: Session,
        delay_days: int = 3,
        num_messages: int = 2
    ) -> Dict:
        """
        Schedule follow-up WhatsApp messages
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            delay_days: Days between messages
            num_messages: Number of follow-up messages
            
        Returns:
            Scheduling result
        """
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead or not lead.phone:
            return {"success": False, "error": "Lead not found or no phone"}
        
        scheduled = []
        for i in range(num_messages):
            send_date = datetime.utcnow() + timedelta(days=delay_days * (i + 1))
            scheduled.append({
                "message_number": i + 1,
                "scheduled_date": send_date.isoformat(),
                "template": "follow_up"
            })
        
        # Log scheduling
        activity = Activity(
            company_id=company_id,
            lead_id=lead_id,
            activity_type="whatsapp",
            title=f"WhatsApp Follow-ups Scheduled",
            description=f"{num_messages} follow-up messages scheduled, {delay_days} days apart",
            user_id=lead.assigned_to or lead.created_by,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "lead_id": lead_id,
            "scheduled_messages": scheduled
        }
    
    @staticmethod
    def get_whatsapp_analytics(company_id: int, db: Session, days: int = 30) -> Dict:
        """
        Get WhatsApp messaging analytics
        
        Args:
            company_id: Company ID
            db: Database session
            days: Number of days to analyze
            
        Returns:
            WhatsApp analytics
        """
        from sqlalchemy import func
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get WhatsApp activities
        wa_activities = db.query(Activity).filter(
            Activity.company_id == company_id,
            Activity.activity_type == "whatsapp",
            Activity.activity_date >= cutoff
        ).all()
        
        sent = len([a for a in wa_activities if "sent" in (a.title or "").lower()])
        received = len([a for a in wa_activities if "received" in (a.title or "").lower()])
        
        return {
            "period_days": days,
            "total_messages": len(wa_activities),
            "sent": sent,
            "received": received,
            "response_rate": round((received / sent * 100), 2) if sent > 0 else 0
        }
