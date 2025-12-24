"""
Email Sequence Model
Drip campaign email sequences for lead nurturing
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class EmailSequence(Base):
    """Email sequence template model"""
    
    __tablename__ = "email_sequences"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Sequence Information
    name = Column(String(255), nullable=False)  # e.g., "Welcome Sequence", "Nurturing Sequence"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Trigger Conditions
    trigger_on_creation = Column(Boolean, default=True, nullable=False)  # Trigger on lead creation
    trigger_score_threshold = Column(Integer, nullable=True)  # Trigger when score reaches threshold
    
    # Sequence Configuration
    total_emails = Column(Integer, default=5, nullable=False)  # Number of emails in sequence
    sequence_duration_days = Column(Integer, default=14, nullable=False)  # Total duration in days
    
    # Email Templates (JSON array)
    email_templates = Column(JSON, nullable=True)  # Array of email templates with delay days
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company")
    sequence_emails = relationship("EmailSequenceEmail", back_populates="sequence", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EmailSequence {self.name}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "trigger_on_creation": self.trigger_on_creation,
            "trigger_score_threshold": self.trigger_score_threshold,
            "total_emails": self.total_emails,
            "sequence_duration_days": self.sequence_duration_days,
            "email_templates": self.email_templates,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EmailSequenceEmail(Base):
    """Individual email in a sequence"""
    
    __tablename__ = "email_sequence_emails"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    sequence_id = Column(Integer, ForeignKey("email_sequences.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Email Information
    email_number = Column(Integer, nullable=False)  # 1, 2, 3, 4, 5
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    
    # Scheduling
    delay_days = Column(Integer, default=0, nullable=False)  # Days after sequence start
    scheduled_send_date = Column(DateTime, nullable=True)
    actual_send_date = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, sent, opened, clicked, bounced, failed
    
    # Tracking
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    open_count = Column(Integer, default=0, nullable=False)
    click_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    sequence = relationship("EmailSequence", back_populates="sequence_emails")
    lead = relationship("Lead")
    
    def __repr__(self):
        return f"<EmailSequenceEmail {self.email_number} for Lead {self.lead_id}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "sequence_id": self.sequence_id,
            "lead_id": self.lead_id,
            "email_number": self.email_number,
            "subject": self.subject,
            "delay_days": self.delay_days,
            "scheduled_send_date": self.scheduled_send_date.isoformat() if self.scheduled_send_date else None,
            "actual_send_date": self.actual_send_date.isoformat() if self.actual_send_date else None,
            "status": self.status,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "clicked_at": self.clicked_at.isoformat() if self.clicked_at else None,
            "open_count": self.open_count,
            "click_count": self.click_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

