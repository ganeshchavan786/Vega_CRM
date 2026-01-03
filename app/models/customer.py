"""
Customer Model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Customer(Base):
    """Customer/Client model"""
    
    __tablename__ = "customers"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Customer Code
    customer_code = Column(String(50), nullable=True, index=True)
    
    # Unique ID (v2.1.0 feature)
    unique_id = Column(String(50), nullable=True, unique=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    secondary_phone = Column(String(20), nullable=True)
    
    # Address Information
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    
    # Customer Type & Status (Enterprise: Account Model)
    customer_type = Column(String(50), default="individual", nullable=False, index=True)  # individual, business
    account_type = Column(String(50), nullable=True, index=True)  # customer, prospect, partner, competitor, reseller
    status = Column(String(20), default="active", nullable=False, index=True)  # active, inactive, prospect, lost
    
    # Business Information (if business customer)
    industry = Column(String(100), nullable=True)
    company_name = Column(String(255), nullable=True)
    company_size = Column(String(100), nullable=True)  # 50-100 Employees, etc.
    annual_revenue = Column(Numeric(15, 2), nullable=True)  # Annual revenue
    gstin = Column(String(15), nullable=True, index=True)  # GSTIN number
    website = Column(String(255), nullable=True)
    
    # Account Health & Lifecycle (Enterprise Fields)
    health_score = Column(String(20), nullable=True, index=True)  # green, yellow, red, black
    lifecycle_stage = Column(String(50), nullable=True, index=True)  # MQA, SQA, Customer, Churned
    is_active = Column(Boolean, default=True, nullable=False)  # Enterprise rule: never delete, use inactive flag
    
    # Account Owner (Enterprise)
    account_owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Additional Information
    source = Column(String(100), nullable=True)  # Lead source
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high
    credit_limit = Column(Numeric(15, 2), default=0, nullable=False)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Assignment
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="customers")
    creator = relationship("User", foreign_keys=[created_by], back_populates="customers_created")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="customers_assigned")
    account_owner = relationship("User", foreign_keys=[account_owner_id])
    
    def __repr__(self):
        return f"<Customer {self.name}>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "customer_code": self.customer_code,
            "unique_id": self.unique_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "secondary_phone": self.secondary_phone,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zip_code": self.zip_code,
            "customer_type": self.customer_type,
            "account_type": self.account_type,
            "status": self.status,
            "industry": self.industry,
            "company_name": self.company_name,
            "company_size": self.company_size,
            "annual_revenue": float(self.annual_revenue) if self.annual_revenue else None,
            "gstin": self.gstin,
            "website": self.website,
            "health_score": self.health_score,
            "lifecycle_stage": self.lifecycle_stage,
            "is_active": self.is_active,
            "account_owner_id": self.account_owner_id,
            "source": self.source,
            "priority": self.priority,
            "credit_limit": float(self.credit_limit) if self.credit_limit else 0,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            if self.creator:
                data["created_by"] = {
                    "id": self.creator.id,
                    "name": self.creator.full_name,
                    "email": self.creator.email
                }
            
            if self.assigned_user:
                data["assigned_to"] = {
                    "id": self.assigned_user.id,
                    "name": self.assigned_user.full_name,
                    "email": self.assigned_user.email
                }
        
        return data

