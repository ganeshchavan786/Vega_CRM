"""
Audit Trail Model
Tracks all important changes and activities in the system
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class AuditTrail(Base):
    __tablename__ = "audit_trails"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # User information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)  # For quick reference even if user deleted
    
    # Action details
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    resource_type = Column(String(100), nullable=False, index=True)  # Customer, Lead, Deal, Task, Activity, User, etc.
    resource_id = Column(Integer, nullable=True, index=True)  # ID of the affected resource
    
    # Change tracking
    old_values = Column(JSON, nullable=True)  # Previous values (for UPDATE)
    new_values = Column(JSON, nullable=True)  # New values (for CREATE/UPDATE)
    
    # Request information
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)  # Browser/Device info
    
    # Status and details
    status = Column(String(20), default="SUCCESS", nullable=False, index=True)  # SUCCESS, FAILED, PARTIAL
    message = Column(Text, nullable=True)  # Human-readable description
    details = Column(JSON, nullable=True)  # Additional context
    
    # Relationships
    user = relationship("User", backref="audit_trails")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_action_timestamp', 'action', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditTrail(id={self.id}, action='{self.action}', resource='{self.resource_type}', user='{self.user_email}', timestamp='{self.timestamp}')>"

