"""
Report Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False, index=True)  # sales, leads, activities, custom
    
    # Report configuration
    config = Column(JSON, nullable=True)  # Filters, columns, grouping, etc.
    query_template = Column(Text, nullable=True)  # SQL or query template
    
    # Access control
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)  # Available to all users in company
    allowed_roles = Column(JSON, nullable=True)  # List of roles that can access
    
    # Schedule
    is_scheduled = Column(Boolean, default=False)
    schedule_cron = Column(String(100), nullable=True)  # Cron expression
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", backref="reports")
    creator = relationship("User", backref="created_reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, name='{self.name}', type='{self.report_type}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "report_type": self.report_type,
            "config": self.config,
            "company_id": self.company_id,
            "created_by": self.created_by,
            "is_public": self.is_public,
            "allowed_roles": self.allowed_roles,
            "is_scheduled": self.is_scheduled,
            "schedule_cron": self.schedule_cron,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
