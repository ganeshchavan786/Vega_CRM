"""
Lead Model - Enterprise Lead Management
Enhanced with attribution, scoring, and qualification fields
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class LeadStatus(str, enum.Enum):
    """Lead status enumeration"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"
    RECYCLED = "recycled"
    DISQUALIFIED = "disqualified"


class LeadStage(str, enum.Enum):
    """Lead stage enumeration"""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    CONVERTED = "converted"


class AuthorityLevel(str, enum.Enum):
    """Authority level enumeration"""
    DECISION_MAKER = "decision_maker"
    INFLUENCER = "influencer"
    USER = "user"
    GATEKEEPER = "gatekeeper"


class Lead(Base):
    """Enterprise Lead model with attribution, scoring, and qualification"""
    
    __tablename__ = "leads"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    converted_to_account_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Basic Information (Enterprise Model)
    first_name = Column(String(100), nullable=True)  # Allow null for backward compatibility
    last_name = Column(String(100), nullable=True)  # Allow null for backward compatibility
    company_name = Column(String(200), nullable=True)  # Allow null for backward compatibility
    email = Column(String(255), nullable=True, index=True)  # Allow null for backward compatibility
    phone = Column(String(20), nullable=True, index=True)  # Allow null for backward compatibility
    country = Column(String(100), default="India", nullable=True)
    
    # Legacy field for backward compatibility
    lead_name = Column(String(255), nullable=True)  # Computed from first_name + last_name
    
    # Source Attribution (Mandatory Fields for new leads)
    source = Column(String(100), nullable=True)  # lead_source (Google Ads, Website, etc.)
    campaign = Column(String(200), nullable=True)  # Campaign name
    medium = Column(String(50), nullable=True)  # CPC, Email, Social
    term = Column(String(200), nullable=True)  # Search term
    
    # Lead Management
    lead_owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # Assigned SDR
    status = Column(String(50), default="new", nullable=False, index=True)  # Using string for backward compatibility, can use Enum later
    stage = Column(String(50), default="awareness", nullable=True)  # Using string for backward compatibility
    lead_score = Column(Integer, default=0, nullable=True)  # 0-100 ML-based score
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high
    
    # Qualification Fields
    interest_product = Column(String(200), nullable=True)
    budget_range = Column(String(100), nullable=True)
    authority_level = Column(String(50), nullable=True)  # Using string for backward compatibility
    timeline = Column(String(100), nullable=True)  # 3-6 Months, 60 Days, etc.
    
    # Privacy & Compliance
    gdpr_consent = Column(Boolean, default=False, nullable=True)
    dnd_status = Column(Boolean, default=False, nullable=True)
    opt_in_date = Column(DateTime, nullable=True)
    
    # System Flags
    is_duplicate = Column(Boolean, default=False, nullable=True)
    spam_score = Column(Integer, default=0, nullable=True)  # 0-100
    validation_status = Column(String(50), default="pending", nullable=True)
    
    # Lead Value
    estimated_value = Column(Numeric(15, 2), nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    industry = Column(String(100), nullable=True)
    
    # Assignment (Legacy fields for backward compatibility)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    converted_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company")
    customer = relationship("Customer", foreign_keys=[customer_id])
    converted_account = relationship("Customer", foreign_keys=[converted_to_account_id])
    lead_owner = relationship("User", foreign_keys=[lead_owner_id])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    deals = relationship("Deal", back_populates="lead")
    
    def __repr__(self):
        if self.first_name and self.last_name:
            return f"<Lead {self.first_name} {self.last_name} - {self.company_name}>"
        return f"<Lead {self.lead_name}>"
    
    @property
    def full_name(self):
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.lead_name or ""
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            "id": self.id,
            "company_id": self.company_id,
            "customer_id": self.customer_id,
            "converted_to_account_id": self.converted_to_account_id,
            
            # Basic Information
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "company_name": self.company_name,
            "email": self.email,
            "phone": self.phone,
            "country": self.country or "India",
            "lead_name": self.lead_name or self.full_name,  # Backward compatibility
            
            # Attribution
            "source": self.source,
            "campaign": self.campaign,
            "medium": self.medium,
            "term": self.term,
            
            # Lead Management
            "lead_owner_id": self.lead_owner_id,
            "status": self.status,
            "stage": self.stage,
            "lead_score": self.lead_score or 0,
            "priority": self.priority,
            
            # Qualification
            "interest_product": self.interest_product,
            "budget_range": self.budget_range,
            "authority_level": self.authority_level,
            "timeline": self.timeline,
            
            # Compliance
            "gdpr_consent": self.gdpr_consent or False,
            "dnd_status": self.dnd_status or False,
            "opt_in_date": self.opt_in_date.isoformat() if self.opt_in_date else None,
            
            # System Flags
            "is_duplicate": self.is_duplicate or False,
            "spam_score": self.spam_score or 0,
            "validation_status": self.validation_status or "pending",
            
            # Legacy Fields
            "estimated_value": float(self.estimated_value) if self.estimated_value else None,
            "notes": self.notes,
            "industry": self.industry,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            
            # Timestamps
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "converted_at": self.converted_at.isoformat() if self.converted_at else None,
        }
        
        if include_relations:
            if self.lead_owner:
                data["lead_owner"] = {
                    "id": self.lead_owner.id,
                    "name": self.lead_owner.full_name,
                    "email": self.lead_owner.email
                }
            if self.assigned_user:
                data["assigned_user"] = {
                    "id": self.assigned_user.id,
                    "name": self.assigned_user.full_name,
                    "email": self.assigned_user.email
                }
            if self.creator:
                data["creator"] = {
                    "id": self.creator.id,
                    "name": self.creator.full_name,
                    "email": self.creator.email
                }
        
        return data
