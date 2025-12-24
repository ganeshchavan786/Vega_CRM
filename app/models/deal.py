"""
Deal Model - Sales Pipeline Deal Tracking
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Deal(Base):
    """Deal/Opportunity model for sales pipeline"""
    
    __tablename__ = "deals"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)  # Enterprise: link to account
    primary_contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)  # Enterprise: primary contact
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Deal Information
    deal_name = Column(String(255), nullable=False)
    deal_value = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    
    # Pipeline Stage
    stage = Column(String(50), default="prospect", nullable=False, index=True)
    # Stages: prospect, qualified, proposal, negotiation, closed_won, closed_lost
    probability = Column(Integer, default=0, nullable=False)  # Win probability percentage (0-100)
    forecast_category = Column(String(50), nullable=True)  # best_case, commit, most_likely, worst_case
    
    # Dates
    expected_close_date = Column(Date, nullable=True)
    actual_close_date = Column(Date, nullable=True)
    
    # Status
    status = Column(String(50), default="open", nullable=False, index=True)  # open, won, lost
    loss_reason = Column(Text, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company")
    customer = relationship("Customer", foreign_keys=[customer_id])
    account = relationship("Customer", foreign_keys=[account_id])
    primary_contact = relationship("Contact", foreign_keys=[primary_contact_id])
    lead = relationship("Lead", back_populates="deals")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Deal {self.deal_name}>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "customer_id": self.customer_id,
            "lead_id": self.lead_id,
            "deal_name": self.deal_name,
            "deal_value": float(self.deal_value) if self.deal_value else 0,
            "currency": self.currency,
            "stage": self.stage,
            "probability": self.probability,
            "forecast_category": self.forecast_category,
            "account_id": self.account_id,
            "primary_contact_id": self.primary_contact_id,
            "expected_close_date": self.expected_close_date.isoformat() if self.expected_close_date else None,
            "actual_close_date": self.actual_close_date.isoformat() if self.actual_close_date else None,
            "status": self.status,
            "loss_reason": self.loss_reason,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            if self.customer:
                data["customer"] = {
                    "id": self.customer.id,
                    "name": self.customer.name,
                    "email": self.customer.email
                }
            
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
        
        return data

