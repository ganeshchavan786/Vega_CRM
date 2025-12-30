"""
Permission Utilities
Role-Based Access Control (RBAC) helper functions
"""

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.models.user_company import UserCompany
from app.models.permission import Permission, RolePermission
from app.database import get_db
from app.utils.dependencies import get_current_active_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require admin or super_admin role
    """
    if current_user.role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_manager(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require manager, admin, or super_admin role
    """
    if current_user.role not in ["super_admin", "admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )
    return current_user


def require_super_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to require super_admin role
    """
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def check_company_admin(user_id: int, company_id: int, db: Session) -> bool:
    """
    Check if user is admin in the company
    
    Args:
        user_id: User ID
        company_id: Company ID
        db: Database session
        
    Returns:
        True if user is admin, False otherwise
    """
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id,
        UserCompany.role == "admin"
    ).first()
    
    return user_company is not None


def check_company_access(user_id: int, company_id: int, db: Session) -> bool:
    """
    Check if user has any access to the company
    
    Args:
        user_id: User ID
        company_id: Company ID
        db: Database session
        
    Returns:
        True if user has access, False otherwise
    """
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id
    ).first()
    
    return user_company is not None


def get_company_role(user_id: int, company_id: int, db: Session) -> Optional[str]:
    """
    Get user's role in a specific company
    
    Args:
        user_id: User ID
        company_id: Company ID
        db: Database session
        
    Returns:
        Role name or None if user doesn't belong to company
    """
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id
    ).first()
    
    return user_company.role if user_company else None


def has_permission(
    user: User,
    resource: str,
    action: str,
    company_id: Optional[int] = None,
    db: Optional[Session] = None
) -> bool:
    """
    Check if user has permission for a resource-action combination
    
    This function checks permissions in the following order:
    1. Super admin always has all permissions
    2. Check database role_permissions table (global or company-specific)
    3. Fallback to hardcoded role-based logic if no database permissions found
    
    Args:
        user: User object
        resource: Resource name (e.g., "customer", "lead", "deal")
        action: Action name (e.g., "create", "read", "update", "delete")
        company_id: Optional company ID for company-specific permissions
        db: Database session (required for database permission checks)
        
    Returns:
        True if user has permission, False otherwise
    """
    # Super admin always has all permissions
    if user.role == "super_admin":
        return True
    
    # Admin role has all permissions (check company admin if company_id provided)
    if user.role == "admin":
        if company_id and db:
            return check_company_admin(user.id, company_id, db)
        return True
    
    # Check company-specific admin before database check
    if company_id and db:
        company_role = get_company_role(user.id, company_id, db)
        if company_role == "admin":
            return True
    
    # If database session is provided, check database permissions
    if db is not None:
        # Try to find permission in database
        permission = db.query(Permission).filter(
            Permission.resource == resource,
            Permission.action == action
        ).first()
        
        if permission:
            # Get user's role(s) to check
            roles_to_check = []
            
            # Add global role
            if user.role:
                roles_to_check.append(("global", user.role))
            
            # Add company-specific role if company_id provided
            if company_id:
                company_role = get_company_role(user.id, company_id, db)
                if company_role:
                    roles_to_check.append(("company", company_role))
            
            # Check role_permissions table
            for scope, role in roles_to_check:
                role_perm = db.query(RolePermission).filter(
                    RolePermission.permission_id == permission.id,
                    RolePermission.role == role,
                    RolePermission.granted == True
                )
                
                # Filter by scope (global vs company-specific)
                if scope == "company":
                    role_perm = role_perm.filter(RolePermission.company_id == company_id)
                else:
                    role_perm = role_perm.filter(RolePermission.company_id.is_(None))
                
                role_perm = role_perm.first()
                
                if role_perm:
                    return True
            
            # If permission exists in database but no role_permission found,
            # deny access (explicit permission required)
            return False
    
    # Fallback to hardcoded role-based logic if no database session or permission not found
    return _has_permission_fallback(user, resource, action, company_id, db)


def _has_permission_fallback(
    user: User,
    resource: str,
    action: str,
    company_id: Optional[int] = None,
    db: Optional[Session] = None
) -> bool:
    """
    Fallback permission logic using hardcoded role-based rules
    
    This is used when:
    - Database session is not provided
    - Permission not found in database
    - Migration not yet run
    
    Args:
        user: User object
        resource: Resource name
        action: Action name
        company_id: Optional company ID
        db: Optional database session
        
    Returns:
        True if user has permission based on role, False otherwise
    """
    # Super admin always has all permissions
    if user.role == "super_admin":
        return True
    
    # Admin role has all permissions
    if user.role == "admin":
        return True
    
    # Check company-specific admin
    if company_id and db:
        if check_company_admin(user.id, company_id, db):
            return True
    
    # Manager role - most permissions, restricted deletes
    if user.role == "manager":
        # Managers cannot delete users or companies
        if resource in ["user", "company"] and action == "delete":
            return False
        return True
    
    # Sales rep role - most permissions, restricted deletes
    if user.role == "sales_rep":
        # Sales reps cannot delete users, companies, or deals
        if resource in ["user", "company"] and action == "delete":
            return False
        if resource == "deal" and action == "delete":
            return False
        return True
    
    # User role - read-only
    if user.role == "user":
        return action == "read"
    
    # Default: no permission
    return False


def check_permission(
    user: User,
    resource: str,
    action: str,
    company_id: Optional[int] = None,
    db: Optional[Session] = None
):
    """
    Check permission and raise HTTPException if denied
    
    Args:
        user: User object
        resource: Resource name
        action: Action name
        company_id: Optional company ID
        db: Optional database session
        
    Raises:
        HTTPException: If permission denied
    """
    if not has_permission(user, resource, action, company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {resource}:{action}"
        )


# Permission definitions for consistency
PERMISSIONS = {
    "customer": ["create", "read", "update", "delete"],
    "lead": ["create", "read", "update", "delete", "convert"],
    "deal": ["create", "read", "update", "delete"],
    "task": ["create", "read", "update", "delete"],
    "activity": ["create", "read", "update", "delete"],
    "contact": ["create", "read", "update", "delete"],
    "user": ["create", "read", "update", "delete"],
    "company": ["create", "read", "update", "delete"],
}


def require_company_admin(company_id: int):
    """
    Dependency factory to require company admin role
    
    Usage:
        @router.get("/{company_id}/users")
        async def get_users(
            company_id: int,
            current_user: User = Depends(require_company_admin(company_id))
        ):
            ...
    """
    def _check_admin(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)) -> User:
        # Super admin has access to all companies
        if current_user.role == "super_admin":
            return current_user
        
        # Check if user is admin in this company
        if not check_company_admin(current_user.id, company_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company admin access required"
            )
        
        return current_user
    
    return _check_admin
