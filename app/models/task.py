"""
Task Model - Task Management
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Task(Base):
    """Task model for task management and tracking"""
    
    __tablename__ = "tasks"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Unique ID (v2.1.0 feature)
    unique_id = Column(String(50), nullable=True, unique=True, index=True)
    
    # Task Information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(50), default="general", nullable=False)  # call, email, meeting, general, follow_up
    
    # Priority & Status
    priority = Column(String(20), default="medium", nullable=False, index=True)  # low, medium, high, urgent
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, in_progress, completed, cancelled
    
    # Dates
    due_date = Column(DateTime, nullable=True, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Related Entities (optional)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company")
    customer = relationship("Customer")
    lead = relationship("Lead")
    deal = relationship("Deal")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Task {self.title}>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "unique_id": self.unique_id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "customer_id": self.customer_id,
            "lead_id": self.lead_id,
            "deal_id": self.deal_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            if self.assigned_user:
                data["assigned_to"] = {
                    "id": self.assigned_user.id,
                    "name": self.assigned_user.full_name,
                    "email": self.assigned_user.email
                }
            
            if self.creator:
                data["created_by"] = {
                    "id": self.creator.id,
                    "name": self.creator.full_name,
                    "email": self.creator.email
                }
            
            if self.customer:
                data["customer"] = {
                    "id": self.customer.id,
                    "name": self.customer.name
                }
        
        return data

