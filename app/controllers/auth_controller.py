"""
Authentication Controller
Handles user authentication logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.config import settings


class AuthController:
    """Authentication business logic"""
    
    @staticmethod
    def register_user(user_data: UserRegister, db: Session) -> User:
        """
        Register new user
        
        Args:
            user_data: User registration data
            db: Database session
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role="user",
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def login_user(login_data: UserLogin, db: Session) -> dict:
        """
        Authenticate user and generate token
        
        Args:
            login_data: Login credentials
            db: Database session
            
        Returns:
            Token and user data
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user.to_dict(include_companies=True)
        }
    
    @staticmethod
    def change_password(user: User, current_password: str, new_password: str, db: Session):
        """
        Change user password
        
        Args:
            user: Current user
            current_password: Current password
            new_password: New password
            db: Database session
            
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        user.password_hash = get_password_hash(new_password)
        db.commit()

