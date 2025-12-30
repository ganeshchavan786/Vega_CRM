"""
Password Reset Token Model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import secrets
from datetime import datetime, timedelta


class PasswordResetToken(Base):
    """Password Reset Token model for forgot password functionality"""
    
    __tablename__ = "password_reset_tokens"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Token
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    # User Reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Expiry
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", backref="password_reset_tokens")
    
    def __repr__(self):
        return f"<PasswordResetToken {self.token[:8]}... for {self.email}>"
    
    @property
    def is_expired(self):
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def get_expiry_time(hours=24):
        """Get expiry time (default 24 hours)"""
        return datetime.utcnow() + timedelta(hours=hours)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "token": self.token,
            "email": self.email,
            "is_used": self.is_used,
            "is_expired": self.is_expired,
            "is_valid": self.is_valid,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
