"""
Permission Controller
Handles permission management business logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.permission import Permission, RolePermission
from app.models.user import User
from app.schemas.permission import (
    PermissionCreate, PermissionUpdate,
    RolePermissionCreate, RolePermissionUpdate, BulkRolePermissionUpdate
)


class PermissionController:
    """Permission management business logic"""
    
    @staticmethod
    def get_permissions(
        db: Session,
        resource: Optional[str] = None,
        action: Optional[str] = None
    ) -> List[Permission]:
        """
        Get all permissions with optional filtering
        
        Args:
            db: Database session
            resource: Optional resource filter
            action: Optional action filter
            
        Returns:
            List of permissions
        """
        query = db.query(Permission)
        
        if resource:
            query = query.filter(Permission.resource == resource)
        
        if action:
            query = query.filter(Permission.action == action)
        
        return query.order_by(Permission.resource, Permission.action).all()
    
    @staticmethod
    def get_permission(permission_id: int, db: Session) -> Permission:
        """
        Get permission by ID
        
        Args:
            permission_id: Permission ID
            db: Database session
            
        Returns:
            Permission object
            
        Raises:
            HTTPException: If permission not found
        """
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        return permission
    
    @staticmethod
    def create_permission(permission_data: PermissionCreate, db: Session) -> Permission:
        """
        Create new permission
        
        Args:
            permission_data: Permission creation data
            db: Database session
            
        Returns:
            Created permission
            
        Raises:
            HTTPException: If permission already exists
        """
        # Check if permission already exists
        existing = db.query(Permission).filter(
            Permission.resource == permission_data.resource,
            Permission.action == permission_data.action
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Permission '{permission_data.resource}:{permission_data.action}' already exists"
            )
        
        permission = Permission(
            resource=permission_data.resource,
            action=permission_data.action,
            description=permission_data.description
        )
        
        db.add(permission)
        db.commit()
        db.refresh(permission)
        
        return permission
    
    @staticmethod
    def update_permission(
        permission_id: int,
        permission_data: PermissionUpdate,
        db: Session
    ) -> Permission:
        """
        Update permission
        
        Args:
            permission_id: Permission ID
            permission_data: Update data
            db: Database session
            
        Returns:
            Updated permission
            
        Raises:
            HTTPException: If permission not found or conflict
        """
        permission = PermissionController.get_permission(permission_id, db)
        
        # Check for conflicts if resource/action is being changed
        if permission_data.resource or permission_data.action:
            new_resource = permission_data.resource or permission.resource
            new_action = permission_data.action or permission.action
            
            existing = db.query(Permission).filter(
                Permission.resource == new_resource,
                Permission.action == new_action,
                Permission.id != permission_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Permission '{new_resource}:{new_action}' already exists"
                )
        
        # Update fields
        update_data = permission_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(permission, key, value)
        
        db.commit()
        db.refresh(permission)
        
        return permission
    
    @staticmethod
    def delete_permission(permission_id: int, db: Session):
        """
        Delete permission (cascades to role_permissions)
        
        Args:
            permission_id: Permission ID
            db: Database session
            
        Raises:
            HTTPException: If permission not found
        """
        permission = PermissionController.get_permission(permission_id, db)
        
        db.delete(permission)
        db.commit()
    
    @staticmethod
    def get_role_permissions(
        db: Session,
        role: Optional[str] = None,
        company_id: Optional[int] = None,
        permission_id: Optional[int] = None
    ) -> List[RolePermission]:
        """
        Get role permissions with optional filtering
        
        Args:
            db: Database session
            role: Optional role filter
            company_id: Optional company filter
            permission_id: Optional permission filter
            
        Returns:
            List of role permissions
        """
        query = db.query(RolePermission)
        
        if role:
            query = query.filter(RolePermission.role == role)
        
        if company_id is not None:
            query = query.filter(RolePermission.company_id == company_id)
        
        if permission_id:
            query = query.filter(RolePermission.permission_id == permission_id)
        
        return query.all()
    
    @staticmethod
    def create_role_permission(
        role_permission_data: RolePermissionCreate,
        db: Session
    ) -> RolePermission:
        """
        Create role permission
        
        Args:
            role_permission_data: Role permission creation data
            db: Database session
            
        Returns:
            Created role permission
            
        Raises:
            HTTPException: If permission or role permission already exists
        """
        # Check if permission exists
        permission = PermissionController.get_permission(role_permission_data.permission_id, db)
        
        # Check if role permission already exists
        existing = db.query(RolePermission).filter(
            RolePermission.permission_id == role_permission_data.permission_id,
            RolePermission.role == role_permission_data.role,
            RolePermission.company_id == role_permission_data.company_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role permission already exists"
            )
        
        role_permission = RolePermission(
            permission_id=role_permission_data.permission_id,
            role=role_permission_data.role,
            company_id=role_permission_data.company_id,
            granted=role_permission_data.granted
        )
        
        db.add(role_permission)
        db.commit()
        db.refresh(role_permission)
        
        return role_permission
    
    @staticmethod
    def update_role_permission(
        role_permission_id: int,
        role_permission_data: RolePermissionUpdate,
        db: Session
    ) -> RolePermission:
        """
        Update role permission
        
        Args:
            role_permission_id: Role permission ID
            role_permission_data: Update data
            db: Database session
            
        Returns:
            Updated role permission
            
        Raises:
            HTTPException: If role permission not found
        """
        role_permission = db.query(RolePermission).filter(
            RolePermission.id == role_permission_id
        ).first()
        
        if not role_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role permission not found"
            )
        
        # Update fields
        update_data = role_permission_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(role_permission, key, value)
        
        db.commit()
        db.refresh(role_permission)
        
        return role_permission
    
    @staticmethod
    def bulk_update_role_permissions(
        bulk_data: BulkRolePermissionUpdate,
        db: Session
    ) -> List[RolePermission]:
        """
        Bulk update role permissions
        
        Args:
            bulk_data: Bulk update data
            db: Database session
            
        Returns:
            List of updated role permissions
        """
        updated_permissions = []
        
        for perm_update in bulk_data.permission_updates:
            permission_id = perm_update.get("permission_id")
            granted = perm_update.get("granted", True)
            
            if not permission_id:
                continue
            
            # Find or create role permission
            role_permission = db.query(RolePermission).filter(
                RolePermission.permission_id == permission_id,
                RolePermission.role == bulk_data.role,
                RolePermission.company_id == bulk_data.company_id
            ).first()
            
            if role_permission:
                role_permission.granted = granted
            else:
                role_permission = RolePermission(
                    permission_id=permission_id,
                    role=bulk_data.role,
                    company_id=bulk_data.company_id,
                    granted=granted
                )
                db.add(role_permission)
            
            updated_permissions.append(role_permission)
        
        db.commit()
        
        # Refresh all
        for perm in updated_permissions:
            db.refresh(perm)
        
        return updated_permissions
    
    @staticmethod
    def delete_role_permission(role_permission_id: int, db: Session):
        """
        Delete role permission
        
        Args:
            role_permission_id: Role permission ID
            db: Database session
            
        Raises:
            HTTPException: If role permission not found
        """
        role_permission = db.query(RolePermission).filter(
            RolePermission.id == role_permission_id
        ).first()
        
        if not role_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role permission not found"
            )
        
        db.delete(role_permission)
        db.commit()
    
    @staticmethod
    def copy_global_to_company(company_id: int, db: Session) -> int:
        """
        Copy all global role permissions to a specific company
        
        Args:
            company_id: Target company ID
            db: Database session
            
        Returns:
            Number of permissions copied
        """
        # Get all global role permissions (where company_id is NULL)
        global_permissions = db.query(RolePermission).filter(
            RolePermission.company_id.is_(None)
        ).all()
        
        copied_count = 0
        
        for global_perm in global_permissions:
            # Check if company-specific permission already exists
            existing = db.query(RolePermission).filter(
                RolePermission.permission_id == global_perm.permission_id,
                RolePermission.role == global_perm.role,
                RolePermission.company_id == company_id
            ).first()
            
            if existing:
                # Update existing
                existing.granted = global_perm.granted
            else:
                # Create new company-specific permission
                new_perm = RolePermission(
                    permission_id=global_perm.permission_id,
                    role=global_perm.role,
                    company_id=company_id,
                    granted=global_perm.granted
                )
                db.add(new_perm)
            
            copied_count += 1
        
        db.commit()
        return copied_count

