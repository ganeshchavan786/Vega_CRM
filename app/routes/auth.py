"""
Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, ChangePassword, ForgotPasswordRequest, ResetPasswordRequest, VerifyResetTokenRequest
from app.controllers.auth_controller import AuthController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response, error_response
from app.models.user import User

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register new user
    
    - **email**: Valid email address (unique)
    - **password**: Min 8 characters, 1 uppercase, 1 lowercase, 1 digit
    - **first_name**: First name (2-100 characters)
    - **last_name**: Last name (2-100 characters)
    - **phone**: Phone number (optional)
    """
    try:
        user = AuthController.register_user(user_data, db)
        return success_response(
            data=user.to_dict(),
            message="User registered successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    User login
    
    - **email**: User email
    - **password**: User password
    
    Returns JWT access token
    """
    try:
        token_data = AuthController.login_user(login_data, db)
        return success_response(
            data=token_data,
            message="Login successful"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information
    
    Requires: JWT token in Authorization header
    """
    return success_response(
        data=current_user.to_dict(include_companies=True),
        message="User data fetched successfully"
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    User logout
    
    Requires: JWT token in Authorization header
    """
    return success_response(
        data={},
        message="Logged out successfully"
    )


@router.put("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 chars, 1 upper, 1 lower, 1 digit)
    
    Requires: JWT token in Authorization header
    """
    try:
        AuthController.change_password(
            current_user,
            password_data.current_password,
            password_data.new_password,
            db
        )
        return success_response(
            data={},
            message="Password changed successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request password reset
    
    - **email**: User email address
    
    Sends password reset link to email (if email exists)
    """
    try:
        result = AuthController.create_password_reset_token(request.email, db)
        return success_response(
            data=result,
            message="Password reset request processed"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/verify-reset-token")
async def verify_reset_token(request: VerifyResetTokenRequest, db: Session = Depends(get_db)):
    """
    Verify if reset token is valid
    
    - **token**: Reset token from email
    
    Returns token validity status
    """
    try:
        result = AuthController.verify_reset_token(request.token, db)
        return success_response(
            data=result,
            message="Token verification complete"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using token
    
    - **token**: Reset token from email
    - **new_password**: New password (min 8 chars, 1 upper, 1 lower, 1 digit)
    
    Resets password and invalidates token
    """
    try:
        result = AuthController.reset_password(request.token, request.new_password, db)
        return success_response(
            data=result,
            message="Password reset successful"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

