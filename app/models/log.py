"""
Log Model for Activity Logging
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from datetime import datetime
from app.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, DEBUG
    category = Column(String(50), nullable=False, index=True)  # Auth, User Activity, Email, Admin, System, Security
    action = Column(String(100), nullable=False)  # e.g., "Login Success", "Customer Created"
    user_id = Column(Integer, nullable=True, index=True)  # User who performed the action
    user_email = Column(String(100), nullable=True, index=True)  # User email for quick reference
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    details = Column(JSON, nullable=True)  # Additional details as JSON
    status = Column(String(20), nullable=False, default="Success")  # Success, Failed
    message = Column(Text, nullable=False)  # Human-readable log message

    def __repr__(self):
        return f"<Log(id={self.id}, level='{self.level}', category='{self.category}', action='{self.action}', timestamp='{self.timestamp}')>"

