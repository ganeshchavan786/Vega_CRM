"""
Activity Model - Activity Logging and History
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Activity(Base):
    """Activity model for logging interactions and history"""
    
    __tablename__ = "activities"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Unique ID (v2.1.0 feature)
    unique_id = Column(String(50), nullable=True, unique=True, index=True)
    
    # Activity Information
    activity_type = Column(String(50), nullable=False, index=True)  # call, email, meeting, note, status_change
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Activity Details
    duration = Column(Integer, nullable=True)  # Duration in minutes
    outcome = Column(String(100), nullable=True)  # positive, negative, neutral, follow_up_required
    
    # Related Entities (optional)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # User who performed activity
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    activity_date = Column(DateTime, nullable=False, index=True)  # When activity occurred
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company")
    customer = relationship("Customer")
    lead = relationship("Lead")
    deal = relationship("Deal")
    task = relationship("Task")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Activity {self.activity_type}: {self.title}>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "unique_id": self.unique_id,
            "activity_type": self.activity_type,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "outcome": self.outcome,
            "customer_id": self.customer_id,
            "lead_id": self.lead_id,
            "deal_id": self.deal_id,
            "task_id": self.task_id,
            "activity_date": self.activity_date.isoformat() if self.activity_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_relations:
            if self.user:
                data["user"] = {
                    "id": self.user.id,
                    "name": self.user.full_name,
                    "email": self.user.email
                }
            
            if self.customer:
                data["customer"] = {
                    "id": self.customer.id,
                    "name": self.customer.name
                }
            
            if self.lead:
                data["lead"] = {
                    "id": self.lead.id,
                    "name": self.lead.lead_name
                }
            
            if self.deal:
                data["deal"] = {
                    "id": self.deal.id,
                    "name": self.deal.deal_name
                }
        
        return data

