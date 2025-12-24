"""
Contact Model - Multi-Person Model (1 Account : N Contacts)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Contact(Base):
    """Contact model - Multiple contacts per account"""
    
    __tablename__ = "contacts"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic Information
    name = Column(String(200), nullable=False)
    job_title = Column(String(100), nullable=True)
    role = Column(String(50), nullable=True)  # decision_maker, influencer, user, gatekeeper, champion, economic_buyer
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    
    # Communication Preferences
    preferred_channel = Column(String(50), nullable=True)  # email, whatsapp, phone, sms, linkedin
    influence_score = Column(String(20), nullable=True)  # high, medium, low
    
    # Flags
    is_primary_contact = Column(Boolean, default=False, nullable=False)
    
    # Assignment
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company")
    account = relationship("Customer", foreign_keys=[account_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Contact {self.name} (Account: {self.account_id})>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "account_id": self.account_id,
            "name": self.name,
            "job_title": self.job_title,
            "role": self.role,
            "email": self.email,
            "phone": self.phone,
            "preferred_channel": self.preferred_channel,
            "influence_score": self.influence_score,
            "is_primary_contact": self.is_primary_contact,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            if self.account:
                data["account"] = {
                    "id": self.account.id,
                    "name": self.account.name
                }
            if self.creator:
                data["creator"] = {
                    "id": self.creator.id,
                    "name": self.creator.full_name,
                    "email": self.creator.email
                }
        
        return data

