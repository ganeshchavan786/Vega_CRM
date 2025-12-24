"""
Contact Controller
Handles contact management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.contact import Contact
from app.models.customer import Customer
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactController:
    """Contact management business logic"""
    
    @staticmethod
    def get_contacts(
        company_id: int,
        account_id: Optional[int],
        current_user: User,
        db: Session,
        search: Optional[str] = None
    ) -> List[Contact]:
        """
        Get all contacts in company (optionally filtered by account)
        
        Args:
            company_id: Company ID
            account_id: Optional account ID filter
            current_user: Current user
            db: Database session
            search: Search query
            
        Returns:
            List of contacts
        """
        # Check user has access to company
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id
        ).first()
        
        if not user_company:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this company"
            )
        
        query = db.query(Contact).filter(Contact.company_id == company_id)
        
        if account_id:
            query = query.filter(Contact.account_id == account_id)
        
        if search:
            query = query.filter(
                (Contact.name.contains(search)) |
                (Contact.email.contains(search)) |
                (Contact.phone.contains(search)) |
                (Contact.job_title.contains(search))
            )
        
        contacts = query.order_by(
            Contact.is_primary_contact.desc(),
            Contact.created_at.desc()
        ).all()
        return contacts
    
    @staticmethod
    def create_contact(
        company_id: int,
        contact_data: ContactCreate,
        current_user: User,
        db: Session
    ) -> Contact:
        """
        Create new contact
        
        Args:
            company_id: Company ID
            contact_data: Contact creation data
            current_user: Current user
            db: Database session
            
        Returns:
            Created contact
        """
        # Check user has access to company
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id
        ).first()
        
        if not user_company:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this company"
            )
        
        # Verify account exists and belongs to company
        account = db.query(Customer).filter(
            Customer.id == contact_data.account_id,
            Customer.company_id == company_id
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # If setting as primary, unset other primary contacts for this account
        if contact_data.is_primary_contact:
            db.query(Contact).filter(
                Contact.account_id == contact_data.account_id,
                Contact.is_primary_contact == True
            ).update({"is_primary_contact": False})
        
        # Create contact
        contact = Contact(
            company_id=company_id,
            account_id=contact_data.account_id,
            name=contact_data.name,
            job_title=contact_data.job_title,
            role=contact_data.role,
            email=contact_data.email,
            phone=contact_data.phone,
            preferred_channel=contact_data.preferred_channel,
            influence_score=contact_data.influence_score,
            is_primary_contact=contact_data.is_primary_contact or False,
            created_by=current_user.id
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        return contact
    
    @staticmethod
    def get_contact(
        company_id: int,
        contact_id: int,
        current_user: User,
        db: Session
    ) -> Contact:
        """
        Get contact by ID
        
        Args:
            company_id: Company ID
            contact_id: Contact ID
            current_user: Current user
            db: Database session
            
        Returns:
            Contact
        """
        # Check user has access to company
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id
        ).first()
        
        if not user_company:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this company"
            )
        
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.company_id == company_id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        return contact
    
    @staticmethod
    def update_contact(
        company_id: int,
        contact_id: int,
        contact_data: ContactUpdate,
        current_user: User,
        db: Session
    ) -> Contact:
        """
        Update contact
        
        Args:
            company_id: Company ID
            contact_id: Contact ID
            contact_data: Contact update data
            current_user: Current user
            db: Database session
            
        Returns:
            Updated contact
        """
        # Check user has access to company
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id
        ).first()
        
        if not user_company:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this company"
            )
        
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.company_id == company_id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        # If changing account, verify new account exists
        if contact_data.account_id and contact_data.account_id != contact.account_id:
            account = db.query(Customer).filter(
                Customer.id == contact_data.account_id,
                Customer.company_id == company_id
            ).first()
            
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
        
        # If setting as primary, unset other primary contacts
        if contact_data.is_primary_contact is True:
            target_account_id = contact_data.account_id or contact.account_id
            db.query(Contact).filter(
                Contact.account_id == target_account_id,
                Contact.id != contact_id,
                Contact.is_primary_contact == True
            ).update({"is_primary_contact": False})
        
        # Update fields
        update_data = contact_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        
        db.commit()
        db.refresh(contact)
        
        return contact
    
    @staticmethod
    def delete_contact(
        company_id: int,
        contact_id: int,
        current_user: User,
        db: Session
    ) -> bool:
        """
        Delete contact
        
        Args:
            company_id: Company ID
            contact_id: Contact ID
            current_user: Current user
            db: Database session
            
        Returns:
            True if deleted
        """
        # Check user has access to company
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == current_user.id,
            UserCompany.company_id == company_id
        ).first()
        
        if not user_company:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this company"
            )
        
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.company_id == company_id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        
        db.delete(contact)
        db.commit()
        
        return True

