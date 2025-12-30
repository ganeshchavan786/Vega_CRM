"""
User Controller
Handles user management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.user import UserCreate, UserUpdate, UserRoleUpdate
from app.utils.security import get_password_hash
from app.services import audit_service, log_service


class UserController:
    """User management business logic"""
    
    @staticmethod
    def get_company_users(
        company_id: int,
        current_user: User,
        db: Session,
        search: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[User]:
        """
        Get all users in a company
        
        Args:
            company_id: Company ID
            current_user: Current user
            db: Database session
            search: Search query
            role: Filter by role
            
        Returns:
            List of users
        """
        query = db.query(User).join(UserCompany).filter(UserCompany.company_id == company_id)
        
        if search:
            query = query.filter(
                (User.first_name.contains(search)) |
                (User.last_name.contains(search)) |
                (User.email.contains(search))
            )
        
        if role:
            query = query.filter(UserCompany.role == role)
        
        users = query.all()
        return users
    
    @staticmethod
    def create_user(
        company_id: int,
        user_data: UserCreate,
        current_user: User,
        db: Session
    ) -> User:
        """
        Create new user in company
        
        Args:
            company_id: Company ID
            user_data: User creation data
            current_user: Current user
            db: Database session
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email exists or insufficient permissions
        """
        # Check if user has permission (admin/manager)
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id,
            UserCompany.role.in_(["admin", "manager"])
        ).first()
        
        if not user_company and current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Check if email exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role=user_data.role,
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        db.flush()
        
        # Add user to company
        user_company_assoc = UserCompany(
            user_id=new_user.id,
            company_id=company_id,
            role=user_data.role,
            is_primary=True
        )
        db.add(user_company_assoc)
        
        db.commit()
        db.refresh(new_user)
        
        # Log audit trail
        try:
            audit_service.log_create(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="User",
                resource_id=new_user.id,
                new_values={"email": new_user.email, "first_name": new_user.first_name, "last_name": new_user.last_name, "role": user_data.role}
            )
        except Exception:
            pass
        
        return new_user
    
    @staticmethod
    def get_user(user_id: int, company_id: int, current_user: User, db: Session) -> User:
        """
        Get user details
        
        Args:
            user_id: User ID
            company_id: Company ID
            current_user: Current user
            db: Database session
            
        Returns:
            User object
            
        Raises:
            HTTPException: If user not found or no access
        """
        user = db.query(User).join(UserCompany).filter(
            User.id == user_id,
            UserCompany.company_id == company_id
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    
    @staticmethod
    def update_user(
        user_id: int,
        company_id: int,
        user_data: UserUpdate,
        current_user: User,
        db: Session
    ) -> User:
        """
        Update user
        
        Args:
            user_id: User ID
            company_id: Company ID
            user_data: Update data
            current_user: Current user
            db: Database session
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If no permission or user not found
        """
        user = UserController.get_user(user_id, company_id, current_user, db)
        
        # Check permission (admin or self)
        if current_user.id != user_id and current_user.role not in ["admin", "super_admin"]:
            user_company = db.query(UserCompany).filter(
                UserCompany.user_id == current_user.id,
                UserCompany.company_id == company_id,
                UserCompany.role == "admin"
            ).first()
            
            if not user_company:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        
        # Store old values for audit
        old_values = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "role": user.role
        }
        
        # Update user
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        
        # Log audit trail for update
        try:
            audit_service.log_update(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="User",
                resource_id=user.id,
                old_values=old_values,
                new_values=update_data
            )
        except Exception:
            pass
        
        return user
    
    @staticmethod
    def update_user_role(
        user_id: int,
        company_id: int,
        role_data: UserRoleUpdate,
        current_user: User,
        db: Session
    ):
        """
        Update user role in company
        
        Args:
            user_id: User ID
            company_id: Company ID
            role_data: New role data
            current_user: Current user
            db: Database session
            
        Raises:
            HTTPException: If no permission
        """
        # Check if current user is admin
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id,
            UserCompany.role == "admin"
        ).first()
        
        if not user_company and current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update roles"
            )
        
        # Update role
        target_user_company = db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.company_id == company_id
        ).first()
        
        if not target_user_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in company"
            )
        
        target_user_company.role = role_data.role
        db.commit()
    
    @staticmethod
    def delete_user(user_id: int, company_id: int, current_user: User, db: Session):
        """
        Delete user from company
        
        Args:
            user_id: User ID
            company_id: Company ID
            current_user: Current user
            db: Database session
            
        Raises:
            HTTPException: If no permission
        """
        # Check if current user is admin
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id,
            UserCompany.role == "admin"
        ).first()
        
        if not user_company and current_user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete users"
            )
        
        # Remove user from company
        target_user_company = db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.company_id == company_id
        ).first()
        
        if not target_user_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in company"
            )
        
        db.delete(target_user_company)
        db.commit()
        
        # Log audit trail for delete
        try:
            audit_service.log_delete(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="User",
                resource_id=user_id,
                old_values={"user_id": user_id, "company_id": company_id}
            )
        except Exception:
            pass
