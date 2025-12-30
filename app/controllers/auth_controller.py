"""
Authentication Controller
Handles user authentication logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas.auth import UserRegister, UserLogin
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.config import settings
from app.services import log_service, audit_service


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
        is_first_user = db.query(User).count() == 0
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role="super_admin" if is_first_user else "user",
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
            # Log failed login attempt
            try:
                log_service.log_warning(
                    db=db,
                    category="AUTH",
                    action="LOGIN_FAILED",
                    message=f"Failed login attempt for email: {login_data.email}"
                )
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            # Log failed login attempt
            try:
                log_service.log_warning(
                    db=db,
                    category="AUTH",
                    action="LOGIN_FAILED",
                    message=f"Invalid password for user: {user.email}",
                    user_id=user.id,
                    user_email=user.email
                )
            except Exception:
                pass
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
        
        # Log successful login
        try:
            log_service.log_info(
                db=db,
                category="AUTH",
                action="LOGIN_SUCCESS",
                message=f"User logged in successfully: {user.email}",
                user_id=user.id,
                user_email=user.email
            )
            audit_service.create_audit_trail(
                db=db,
                user_id=user.id,
                user_email=user.email,
                action="LOGIN",
                resource_type="User",
                resource_id=user.id,
                message=f"User {user.email} logged in"
            )
        except Exception:
            pass
        
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
    
    @staticmethod
    def create_password_reset_token(email: str, db: Session) -> dict:
        """
        Create password reset token for forgot password
        
        Args:
            email: User email
            db: Database session
            
        Returns:
            Token data with reset URL
            
        Raises:
            HTTPException: If email not found
        """
        # Get user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists - security best practice
            # But log it for admin
            try:
                log_service.log_warning(
                    db=db,
                    category="AUTH",
                    action="PASSWORD_RESET_REQUEST",
                    message=f"Password reset requested for non-existent email: {email}"
                )
            except Exception:
                pass
            # Return success anyway to prevent email enumeration
            return {
                "message": "If the email exists, a password reset link has been sent",
                "email": email
            }
        
        # Invalidate any existing tokens for this user
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False
        ).update({"is_used": True})
        
        # Create new token
        token = PasswordResetToken.generate_token()
        reset_token = PasswordResetToken(
            token=token,
            user_id=user.id,
            email=user.email,
            expires_at=PasswordResetToken.get_expiry_time(hours=24)
        )
        
        db.add(reset_token)
        db.commit()
        
        # Log the request
        try:
            log_service.log_info(
                db=db,
                category="AUTH",
                action="PASSWORD_RESET_REQUEST",
                message=f"Password reset token created for: {email}",
                user_id=user.id,
                user_email=user.email
            )
        except Exception:
            pass
        
        return {
            "message": "If the email exists, a password reset link has been sent",
            "email": email,
            "token": token,  # In production, this would be sent via email only
            "user_name": user.full_name,
            "expires_in_hours": 24
        }
    
    @staticmethod
    def verify_reset_token(token: str, db: Session) -> dict:
        """
        Verify if reset token is valid
        
        Args:
            token: Reset token
            db: Database session
            
        Returns:
            Token validity status
        """
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        
        if not reset_token:
            return {
                "valid": False,
                "message": "Invalid or expired reset token"
            }
        
        if reset_token.is_used:
            return {
                "valid": False,
                "message": "This reset token has already been used"
            }
        
        if reset_token.is_expired:
            return {
                "valid": False,
                "message": "This reset token has expired"
            }
        
        return {
            "valid": True,
            "message": "Token is valid",
            "email": reset_token.email
        }
    
    @staticmethod
    def reset_password(token: str, new_password: str, db: Session) -> dict:
        """
        Reset password using token
        
        Args:
            token: Reset token
            new_password: New password
            db: Database session
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If token is invalid
        """
        # Find token
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
        
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        if reset_token.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This reset token has already been used"
            )
        
        if reset_token.is_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This reset token has expired"
            )
        
        # Get user
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.used_at = datetime.utcnow()
        
        db.commit()
        
        # Log the password reset
        try:
            log_service.log_info(
                db=db,
                category="AUTH",
                action="PASSWORD_RESET_SUCCESS",
                message=f"Password reset successful for: {user.email}",
                user_id=user.id,
                user_email=user.email
            )
            audit_service.create_audit_trail(
                db=db,
                user_id=user.id,
                user_email=user.email,
                action="PASSWORD_RESET",
                resource_type="User",
                resource_id=user.id,
                message=f"Password reset for {user.email}"
            )
        except Exception:
            pass
        
        return {
            "message": "Password has been reset successfully",
            "email": user.email
        }
