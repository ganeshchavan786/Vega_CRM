"""
Company Controller
Handles company management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.company import Company
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.services import audit_service


class CompanyController:
    """Company management business logic"""
    
    @staticmethod
    def get_user_companies(user: User, db: Session, search: Optional[str] = None) -> List[Company]:
        """
        Get all companies user has access to
        
        Args:
            user: Current user
            db: Database session
            search: Search query
            
        Returns:
            List of companies
        """
        # Super admin can access all companies
        if user.role == "super_admin":
            query = db.query(Company)
        else:
            query = db.query(Company).join(UserCompany).filter(UserCompany.user_id == user.id)
        
        if search:
            query = query.filter(
                (Company.name.contains(search)) | (Company.email.contains(search))
            )
        
        companies = query.all()
        return companies
    
    @staticmethod
    def create_company(company_data: CompanyCreate, user: User, db: Session) -> Company:
        """
        Create new company
        
        Args:
            company_data: Company creation data
            user: Current user
            db: Database session
            
        Returns:
            Created company
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email exists
        existing = db.query(Company).filter(Company.email == company_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company email already exists"
            )
        
        # Create company
        new_company = Company(**company_data.model_dump())
        db.add(new_company)
        db.flush()
        
        # Add user to company as admin
        user_company = UserCompany(
            user_id=user.id,
            company_id=new_company.id,
            role="admin",
            is_primary=True
        )
        db.add(user_company)
        
        db.commit()
        db.refresh(new_company)
        
        # Log audit trail
        try:
            audit_service.log_create(
                db=db,
                user_id=user.id,
                user_email=user.email,
                resource_type="Company",
                resource_id=new_company.id,
                new_values={"name": new_company.name, "email": new_company.email}
            )
        except Exception:
            pass
        
        return new_company
    
    @staticmethod
    def get_company(company_id: int, user: User, db: Session) -> Company:
        """
        Get company by ID
        
        Args:
            company_id: Company ID
            user: Current user
            db: Database session
            
        Returns:
            Company object
            
        Raises:
            HTTPException: If company not found or no access
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Check if user has access
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == user.id,
            UserCompany.company_id == company_id
        ).first()
        
        if not user_company and user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to this company"
            )
        
        return company
    
    @staticmethod
    def update_company(
        company_id: int,
        company_data: CompanyUpdate,
        user: User,
        db: Session
    ) -> Company:
        """
        Update company
        
        Args:
            company_id: Company ID
            company_data: Update data
            user: Current user
            db: Database session
            
        Returns:
            Updated company
            
        Raises:
            HTTPException: If no permission or company not found
        """
        company = CompanyController.get_company(company_id, user, db)
        
        # Check if user is admin
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == user.id,
            UserCompany.company_id == company_id,
            UserCompany.role == "admin"
        ).first()
        
        if not user_company and user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Store old values for audit
        update_data = company_data.model_dump(exclude_unset=True)
        old_values = {}
        for key in update_data.keys():
            old_values[key] = getattr(company, key, None)
        
        # Update company
        for key, value in update_data.items():
            setattr(company, key, value)
        
        db.commit()
        db.refresh(company)
        
        # Log audit trail
        try:
            audit_service.log_update(
                db=db,
                user_id=user.id,
                user_email=user.email,
                resource_type="Company",
                resource_id=company.id,
                old_values=old_values,
                new_values=update_data
            )
        except Exception:
            pass
        
        return company
    
    @staticmethod
    def delete_company(company_id: int, user: User, db: Session):
        """
        Delete company
        
        Args:
            company_id: Company ID
            user: Current user
            db: Database session
            
        Raises:
            HTTPException: If not super_admin or company not found
        """
        if user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only super admin can delete companies"
            )
        
        company = db.query(Company).filter(Company.id == company_id).first()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        db.delete(company)
        db.commit()
        
        # Log audit trail
        try:
            audit_service.log_delete(
                db=db,
                user_id=user.id,
                user_email=user.email,
                resource_type="Company",
                resource_id=company_id,
                old_values={"name": company.name, "email": company.email}
            )
        except Exception:
            pass

