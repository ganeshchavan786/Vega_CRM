"""
Account Lifecycle Stage Automation
Automatically determines and updates lifecycle stage based on account activity, deals, and status
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional
from app.models.customer import Customer
from app.models.deal import Deal
from app.models.activity import Activity


class LifecycleStageAutomation:
    """Automate lifecycle stage transitions for accounts"""
    
    # Lifecycle Stages
    MQA = "MQA"  # Marketing Qualified Account
    SQA = "SQA"  # Sales Qualified Account
    CUSTOMER = "Customer"  # Active Customer
    CHURNED = "Churned"  # Lost Customer
    
    @staticmethod
    def determine_lifecycle_stage(
        customer: Customer,
        db: Session
    ) -> str:
        """
        Determine lifecycle stage for a customer account
        
        Rules:
        1. If has won deals → Customer
        2. If has open deals in negotiation/proposal → SQA
        3. If has open deals or qualified leads → SQA
        4. If has activities/engagement → MQA
        5. If health score is black and no activity for 90+ days → Churned
        6. Default → MQA (for new accounts)
        
        Args:
            customer: Customer/Account object
            db: Database session
            
        Returns:
            Lifecycle stage: 'MQA', 'SQA', 'Customer', or 'Churned'
        """
        # 1. Check for won deals (Customer)
        won_deals = db.query(Deal).filter(
            and_(
                or_(
                    Deal.customer_id == customer.id,
                    Deal.account_id == customer.id
                ),
                Deal.company_id == customer.company_id,
                Deal.status == "won"
            )
        ).first()
        
        if won_deals:
            return LifecycleStageAutomation.CUSTOMER
        
        # 2. Check for open deals in advanced stages (SQA)
        advanced_deals = db.query(Deal).filter(
            and_(
                or_(
                    Deal.customer_id == customer.id,
                    Deal.account_id == customer.id
                ),
                Deal.company_id == customer.company_id,
                Deal.status == "open",
                Deal.stage.in_(["negotiation", "proposal", "qualified"])
            )
        ).first()
        
        if advanced_deals:
            return LifecycleStageAutomation.SQA
        
        # 3. Check for any open deals (SQA)
        open_deals = db.query(Deal).filter(
            and_(
                or_(
                    Deal.customer_id == customer.id,
                    Deal.account_id == customer.id
                ),
                Deal.company_id == customer.company_id,
                Deal.status == "open"
            )
        ).first()
        
        if open_deals:
            return LifecycleStageAutomation.SQA
        
        # 4. Check for churned status (Black health + no activity for 90+ days)
        if customer.health_score == "black":
            last_activity = db.query(Activity).filter(
                and_(
                    Activity.customer_id == customer.id,
                    Activity.company_id == customer.company_id
                )
            ).order_by(Activity.activity_date.desc()).first()
            
            if last_activity:
                days_since_activity = (datetime.now() - last_activity.activity_date).days
                if days_since_activity >= 90:
                    return LifecycleStageAutomation.CHURNED
            else:
                # No activities at all, check account age
                days_since_creation = (datetime.now() - customer.created_at).days
                if days_since_creation >= 90:
                    return LifecycleStageAutomation.CHURNED
        
        # 5. Check for engagement (MQA)
        recent_activities = db.query(Activity).filter(
            and_(
                Activity.customer_id == customer.id,
                Activity.company_id == customer.company_id,
                Activity.activity_date >= datetime.now() - timedelta(days=90)
            )
        ).first()
        
        if recent_activities:
            return LifecycleStageAutomation.MQA
        
        # 6. Default based on account status
        if customer.status == "lost":
            return LifecycleStageAutomation.CHURNED
        elif customer.status == "prospect":
            return LifecycleStageAutomation.MQA
        elif customer.status == "active":
            # Active but no deals/activities - could be MQA or SQA
            # Check if account has been engaged
            any_activity = db.query(Activity).filter(
                and_(
                    Activity.customer_id == customer.id,
                    Activity.company_id == customer.company_id
                )
            ).first()
            
            if any_activity:
                return LifecycleStageAutomation.MQA
            else:
                return LifecycleStageAutomation.MQA  # Default for new accounts
        
        # Default: MQA
        return LifecycleStageAutomation.MQA
    
    @staticmethod
    def update_lifecycle_stage(
        customer_id: int,
        company_id: int,
        db: Session,
        force_update: bool = False
    ) -> Optional[str]:
        """
        Update lifecycle stage for a customer
        
        Args:
            customer_id: Customer ID
            company_id: Company ID
            db: Database session
            force_update: Force update even if recently calculated
            
        Returns:
            New lifecycle stage or None if not updated
        """
        customer = db.query(Customer).filter(
            and_(
                Customer.id == customer_id,
                Customer.company_id == company_id
            )
        ).first()
        
        if not customer:
            return None
        
        # Determine new lifecycle stage
        new_stage = LifecycleStageAutomation.determine_lifecycle_stage(customer, db)
        
        # Update if different or forced
        if force_update or customer.lifecycle_stage != new_stage:
            old_stage = customer.lifecycle_stage
            customer.lifecycle_stage = new_stage
            db.commit()
            
            # Log stage transition (optional - can create activity log)
            if old_stage != new_stage:
                LifecycleStageAutomation._log_stage_transition(
                    customer, old_stage, new_stage, db
                )
            
            return new_stage
        
        return customer.lifecycle_stage
    
    @staticmethod
    def _log_stage_transition(
        customer: Customer,
        old_stage: Optional[str],
        new_stage: str,
        db: Session
    ):
        """
        Log lifecycle stage transition as an activity
        
        Args:
            customer: Customer object
            old_stage: Previous lifecycle stage
            new_stage: New lifecycle stage
            db: Database session
        """
        try:
            from app.models.activity import Activity
            
            activity = Activity(
                company_id=customer.company_id,
                customer_id=customer.id,
                activity_type="status_change",
                title=f"Lifecycle Stage Changed: {old_stage or 'None'} → {new_stage}",
                description=f"Account lifecycle stage automatically updated from {old_stage or 'None'} to {new_stage}",
                user_id=customer.account_owner_id or customer.assigned_to or customer.created_by,
                activity_date=datetime.now()
            )
            
            db.add(activity)
            db.commit()
        except Exception as e:
            # Don't fail if logging fails
            print(f"Error logging lifecycle stage transition: {e}")
            pass
    
    @staticmethod
    def batch_update_lifecycle_stages(
        company_id: int,
        db: Session,
        customer_ids: Optional[list] = None
    ) -> dict:
        """
        Batch update lifecycle stages for multiple customers
        
        Args:
            company_id: Company ID
            db: Database session
            customer_ids: Optional list of customer IDs to update (None = all)
            
        Returns:
            Dictionary with update statistics
        """
        query = db.query(Customer).filter(Customer.company_id == company_id)
        
        if customer_ids:
            query = query.filter(Customer.id.in_(customer_ids))
        
        customers = query.all()
        
        updated = 0
        unchanged = 0
        
        for customer in customers:
            old_stage = customer.lifecycle_stage
            new_stage = LifecycleStageAutomation.determine_lifecycle_stage(customer, db)
            
            if old_stage != new_stage:
                customer.lifecycle_stage = new_stage
                LifecycleStageAutomation._log_stage_transition(
                    customer, old_stage, new_stage, db
                )
                updated += 1
            else:
                unchanged += 1
        
        db.commit()
        
        return {
            "total": len(customers),
            "updated": updated,
            "unchanged": unchanged
        }
    
    @staticmethod
    def should_auto_transition(
        customer: Customer,
        db: Session
    ) -> bool:
        """
        Check if account should auto-transition lifecycle stage
        
        Args:
            customer: Customer object
            db: Database session
            
        Returns:
            True if should transition, False otherwise
        """
        current_stage = customer.lifecycle_stage
        new_stage = LifecycleStageAutomation.determine_lifecycle_stage(customer, db)
        
        return current_stage != new_stage

