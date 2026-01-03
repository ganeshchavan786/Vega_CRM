"""
Deal Controller
Handles deal/sales pipeline logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.deal import Deal
from app.models.user import User
from app.models.user_company import UserCompany
from app.schemas.deal import DealCreate, DealUpdate
from app.services import audit_service
from app.utils.unique_id import generate_opportunity_id


class DealController:
    """Deal management business logic"""
    
    @staticmethod
    def get_deals(
        company_id: int,
        current_user: User,
        db: Session,
        search: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        assigned_to: Optional[int] = None
    ) -> List[Deal]:
        """Get all deals in company"""
        query = db.query(Deal).filter(Deal.company_id == company_id)
        
        if search:
            query = query.filter(Deal.deal_name.contains(search))
        
        if stage:
            query = query.filter(Deal.stage == stage)
        
        if status:
            query = query.filter(Deal.status == status)
        
        if assigned_to:
            query = query.filter(Deal.assigned_to == assigned_to)
        
        deals = query.order_by(Deal.created_at.desc()).all()
        return deals
    
    @staticmethod
    def create_deal(
        company_id: int,
        deal_data: DealCreate,
        current_user: User,
        db: Session
    ) -> Deal:
        """Create new deal"""
        new_deal = Deal(
            company_id=company_id,
            **deal_data.model_dump(exclude={"assigned_to"}),
            created_by=current_user.id,
            assigned_to=deal_data.assigned_to or current_user.id
        )
        
        db.add(new_deal)
        db.flush()
        
        # Generate unique ID (v2.1.0 feature)
        new_deal.unique_id = generate_opportunity_id(company_id, db=db)
        
        db.commit()
        db.refresh(new_deal)
        
        # Auto-update customer health score and lifecycle stage if deal is linked to customer
        customer_id = new_deal.customer_id or new_deal.account_id
        if customer_id:
            from app.utils.health_score import HealthScoreCalculator
            from app.utils.lifecycle_stage import LifecycleStageAutomation
            
            HealthScoreCalculator.update_health_score(
                customer_id,
                company_id,
                db,
                force_update=True
            )
            
            # Update lifecycle stage (deal creation might change stage to SQA or Customer)
            LifecycleStageAutomation.update_lifecycle_stage(
                customer_id,
                company_id,
                db,
                force_update=True
            )
        
        # Log audit trail
        try:
            audit_service.log_create(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Deal",
                resource_id=new_deal.id,
                new_values={"deal_name": new_deal.deal_name, "amount": new_deal.amount, "stage": new_deal.stage}
            )
        except Exception:
            pass
        
        return new_deal
    
    @staticmethod
    def get_deal(
        deal_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ) -> Deal:
        """Get deal by ID"""
        deal = db.query(Deal).filter(
            Deal.id == deal_id,
            Deal.company_id == company_id
        ).first()
        
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        
        return deal
    
    @staticmethod
    def update_deal(
        deal_id: int,
        company_id: int,
        deal_data: DealUpdate,
        current_user: User,
        db: Session
    ) -> Deal:
        """Update deal"""
        deal = DealController.get_deal(deal_id, company_id, current_user, db)
        
        # Store old customer_id before update
        old_customer_id = deal.customer_id or deal.account_id
        
        # Store old values for audit
        update_data = deal_data.model_dump(exclude_unset=True)
        old_values = {}
        for key in update_data.keys():
            old_values[key] = getattr(deal, key, None)
        
        for key, value in update_data.items():
            setattr(deal, key, value)
        
        db.commit()
        db.refresh(deal)
        
        # Auto-update health score and lifecycle stage for both old and new customer (if changed)
        customer_id = deal.customer_id or deal.account_id
        if customer_id or old_customer_id:
            from app.utils.health_score import HealthScoreCalculator
            from app.utils.lifecycle_stage import LifecycleStageAutomation
            
            if customer_id:
                HealthScoreCalculator.update_health_score(
                    customer_id,
                    company_id,
                    db,
                    force_update=True
                )
                # Update lifecycle stage (deal status change might affect stage)
                LifecycleStageAutomation.update_lifecycle_stage(
                    customer_id,
                    company_id,
                    db,
                    force_update=True
                )
            if old_customer_id and old_customer_id != customer_id:
                HealthScoreCalculator.update_health_score(
                    old_customer_id,
                    company_id,
                    db,
                    force_update=True
                )
                LifecycleStageAutomation.update_lifecycle_stage(
                    old_customer_id,
                    company_id,
                    db,
                    force_update=True
                )
        
        # Log audit trail
        try:
            audit_service.log_update(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Deal",
                resource_id=deal.id,
                old_values=old_values,
                new_values=update_data
            )
        except Exception:
            pass
        
        return deal
    
    @staticmethod
    def delete_deal(
        deal_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ):
        """Delete deal"""
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
        
        deal = db.query(Deal).filter(
            Deal.id == deal_id,
            Deal.company_id == company_id
        ).first()
        
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        
        # Store customer_id before deletion
        customer_id = deal.customer_id or deal.account_id
        
        db.delete(deal)
        db.commit()
        
        # Auto-update customer health score and lifecycle stage after deletion
        if customer_id:
            from app.utils.health_score import HealthScoreCalculator
            from app.utils.lifecycle_stage import LifecycleStageAutomation
            
            HealthScoreCalculator.update_health_score(
                customer_id,
                company_id,
                db,
                force_update=True
            )
            
            LifecycleStageAutomation.update_lifecycle_stage(
                customer_id,
                company_id,
                db,
                force_update=True
            )
        
        # Log audit trail
        try:
            audit_service.log_delete(
                db=db,
                user_id=current_user.id,
                user_email=current_user.email,
                resource_type="Deal",
                resource_id=deal_id,
                old_values={"deal_name": deal.deal_name, "amount": deal.amount}
            )
        except Exception:
            pass
    
    @staticmethod
    def get_deal_stats(company_id: int, db: Session) -> dict:
        """Get deal statistics and pipeline"""
        from sqlalchemy import func
        
        total = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id
        ).scalar()
        
        total_value = db.query(func.sum(Deal.deal_value)).filter(
            Deal.company_id == company_id,
            Deal.status == "open"
        ).scalar()
        
        by_stage = {}
        stages = ["prospect", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]
        for s in stages:
            count = db.query(func.count(Deal.id)).filter(
                Deal.company_id == company_id,
                Deal.stage == s
            ).scalar()
            by_stage[s] = count or 0
        
        won = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.status == "won"
        ).scalar()
        
        return {
            "total_deals": total or 0,
            "total_pipeline_value": float(total_value) if total_value else 0,
            "by_stage": by_stage,
            "deals_won": won or 0
        }

