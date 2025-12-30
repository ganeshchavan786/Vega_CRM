"""
Customer Controller
Handles customer management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.customer import Customer
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.utils.helpers import generate_customer_code
from app.utils.health_score import HealthScoreCalculator
from app.utils.lifecycle_stage import LifecycleStageAutomation
from app.services import audit_service, log_service


class CustomerController:
    """Customer management business logic"""
    
    @staticmethod
    def get_customers(
        company_id: int,
        current_user: User,
        db: Session,
        search: Optional[str] = None,
        status: Optional[str] = None,
        customer_type: Optional[str] = None,
        assigned_to: Optional[int] = None
    ) -> List[Customer]:
        """
        Get all customers in company
        
        Args:
            company_id: Company ID
            current_user: Current user
            db: Database session
            search: Search query
            status: Filter by status
            customer_type: Filter by type
            assigned_to: Filter by assigned user
            
        Returns:
            List of customers
        """
        query = db.query(Customer).filter(Customer.company_id == company_id)
        
        if search:
            query = query.filter(
                (Customer.name.contains(search)) |
                (Customer.email.contains(search)) |
                (Customer.phone.contains(search))
            )
        
        if status:
            query = query.filter(Customer.status == status)
        
        if customer_type:
            query = query.filter(Customer.customer_type == customer_type)
        
        if assigned_to:
            query = query.filter(Customer.assigned_to == assigned_to)
        
        customers = query.order_by(Customer.created_at.desc()).all()
        return customers
    
    @staticmethod
    def create_customer(
        company_id: int,
        customer_data: CustomerCreate,
        current_user: User,
        db: Session
    ) -> Customer:
        """
        Create new customer
        
        Args:
            company_id: Company ID
            customer_data: Customer creation data
            current_user: Current user
            db: Database session
            
        Returns:
            Created customer
        """
        # Create customer
        new_customer = Customer(
            company_id=company_id,
            **customer_data.model_dump(exclude={"assigned_to"}),
            created_by=current_user.id,
            assigned_to=customer_data.assigned_to or current_user.id
        )
        
        db.add(new_customer)
        db.flush()
        
        # Generate customer code
        new_customer.customer_code = generate_customer_code(company_id, new_customer.id)
        
        # Calculate initial health score
        new_customer.health_score = HealthScoreCalculator.calculate_health_score(
            new_customer, db
        )
        
        # Determine initial lifecycle stage
        new_customer.lifecycle_stage = LifecycleStageAutomation.determine_lifecycle_stage(
            new_customer, db
        )
        
        db.commit()
        db.refresh(new_customer)
        
        # Log audit trail
        try:
            audit_service.log_create(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Customer",
                resource_id=new_customer.id,
                new_values={"name": new_customer.name, "email": new_customer.email, "company_id": company_id}
            )
            log_service.log_info(
                db=db,
                category="USER_ACTIVITY",
                action="CREATE_CUSTOMER",
                message=f"Customer '{new_customer.name}' created",
                user_id=current_user.id
            )
        except Exception:
            pass  # Don't fail if audit logging fails
        
        return new_customer
    
    @staticmethod
    def get_customer(
        customer_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ) -> Customer:
        """
        Get customer by ID
        
        Args:
            customer_id: Customer ID
            company_id: Company ID
            current_user: Current user
            db: Database session
            
        Returns:
            Customer object
            
        Raises:
            HTTPException: If customer not found
        """
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == company_id
        ).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return customer
    
    @staticmethod
    def update_customer(
        customer_id: int,
        company_id: int,
        customer_data: CustomerUpdate,
        current_user: User,
        db: Session
    ) -> Customer:
        """
        Update customer
        
        Args:
            customer_id: Customer ID
            company_id: Company ID
            customer_data: Update data
            current_user: Current user
            db: Database session
            
        Returns:
            Updated customer
        """
        customer = CustomerController.get_customer(customer_id, company_id, current_user, db)
        
        # Store old values for audit before update
        update_data = customer_data.model_dump(exclude_unset=True)
        old_values = {}
        for key in update_data.keys():
            old_values[key] = getattr(customer, key, None)
        
        # Update customer
        for key, value in update_data.items():
            setattr(customer, key, value)
        
        # Recalculate health score if status changed or if health_score not explicitly set
        if 'status' in update_data or 'health_score' not in update_data:
            customer.health_score = HealthScoreCalculator.calculate_health_score(
                customer, db
            )
        
        # Recalculate lifecycle stage if status changed, deals changed, or lifecycle_stage not explicitly set
        if 'status' in update_data or 'lifecycle_stage' not in update_data:
            customer.lifecycle_stage = LifecycleStageAutomation.determine_lifecycle_stage(
                customer, db
            )
        
        db.commit()
        db.refresh(customer)
        
        # Log audit trail for update
        try:
            audit_service.log_update(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Customer",
                resource_id=customer.id,
                old_values=old_values,
                new_values=update_data
            )
            log_service.log_info(
                db=db,
                category="USER_ACTIVITY",
                action="UPDATE_CUSTOMER",
                message=f"Customer '{customer.name}' updated",
                user_id=current_user.id
            )
        except Exception:
            pass
        
        return customer
    
    @staticmethod
    def delete_customer(
        customer_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ):
        """
        Delete customer
        
        Args:
            customer_id: Customer ID
            company_id: Company ID
            current_user: Current user
            db: Database session
            
        Raises:
            HTTPException: If no permission or customer not found
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
        
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == company_id
        ).first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        customer_name = customer.name
        db.delete(customer)
        db.commit()
        
        # Log audit trail for delete
        try:
            audit_service.log_delete(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Customer",
                resource_id=customer_id,
                old_values={"name": customer_name, "company_id": company_id}
            )
            log_service.log_info(
                db=db,
                category="USER_ACTIVITY",
                action="DELETE_CUSTOMER",
                message=f"Customer '{customer_name}' deleted",
                user_id=current_user.id
            )
        except Exception:
            pass
    
    @staticmethod
    def get_customer_stats(company_id: int, db: Session) -> dict:
        """
        Get customer statistics for company
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Customer statistics
        """
        from sqlalchemy import func
        
        total = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id
        ).scalar()
        
        active = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.status == "active"
        ).scalar()
        
        inactive = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.status == "inactive"
        ).scalar()
        
        prospect = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.status == "prospect"
        ).scalar()
        
        individual = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.customer_type == "individual"
        ).scalar()
        
        business = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.customer_type == "business"
        ).scalar()
        
        return {
            "total_customers": total or 0,
            "active_customers": active or 0,
            "inactive_customers": inactive or 0,
            "prospect_customers": prospect or 0,
            "by_type": {
                "individual": individual or 0,
                "business": business or 0
            }
        }

