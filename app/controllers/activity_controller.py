"""
Activity Controller
Handles activity logging logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityUpdate


class ActivityController:
    """Activity management business logic"""
    
    @staticmethod
    def get_activities(
        company_id: int,
        current_user: User,
        db: Session,
        activity_type: Optional[str] = None,
        customer_id: Optional[int] = None,
        lead_id: Optional[int] = None,
        deal_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Activity]:
        """Get all activities in company"""
        query = db.query(Activity).filter(Activity.company_id == company_id)
        
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        if customer_id:
            query = query.filter(Activity.customer_id == customer_id)
        
        if lead_id:
            query = query.filter(Activity.lead_id == lead_id)
        
        if deal_id:
            query = query.filter(Activity.deal_id == deal_id)
        
        if user_id:
            query = query.filter(Activity.user_id == user_id)
        
        activities = query.order_by(Activity.activity_date.desc()).all()
        return activities
    
    @staticmethod
    def create_activity(
        company_id: int,
        activity_data: ActivityCreate,
        current_user: User,
        db: Session
    ) -> Activity:
        """Log new activity"""
        new_activity = Activity(
            company_id=company_id,
            **activity_data.model_dump(),
            user_id=current_user.id
        )
        
        db.add(new_activity)
        db.commit()
        db.refresh(new_activity)
        
        # Auto-update customer health score if activity is linked to customer
        if new_activity.customer_id:
            from app.utils.health_score import HealthScoreCalculator
            HealthScoreCalculator.update_health_score(
                new_activity.customer_id,
                company_id,
                db,
                force_update=True
            )
        
        # Auto-increment lead score if activity is linked to lead
        if new_activity.lead_id:
            from app.utils.lead_scoring import LeadScoringAlgorithm
            
            # Determine increment based on activity type and outcome
            increment = 0
            reason = f"{new_activity.activity_type} activity"
            
            if new_activity.activity_type == "email":
                if "opened" in (new_activity.description or "").lower():
                    increment = 5
                    reason = "Email opened"
                elif "clicked" in (new_activity.description or "").lower():
                    increment = 10
                    reason = "Email clicked"
                else:
                    increment = 3
            elif new_activity.activity_type == "call":
                increment = 5
                if new_activity.outcome == "positive":
                    increment += 3
            elif new_activity.activity_type == "meeting":
                increment = 10
                if new_activity.outcome == "positive":
                    increment += 5
            elif new_activity.outcome == "positive":
                increment = 5
            
            if increment > 0:
                LeadScoringAlgorithm.increment_lead_score(
                    new_activity.lead_id,
                    company_id,
                    increment,
                    db,
                    reason=reason
                )
        
        return new_activity
    
    @staticmethod
    def get_activity(
        activity_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ) -> Activity:
        """Get activity by ID"""
        activity = db.query(Activity).filter(
            Activity.id == activity_id,
            Activity.company_id == company_id
        ).first()
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        return activity
    
    @staticmethod
    def update_activity(
        activity_id: int,
        company_id: int,
        activity_data: ActivityUpdate,
        current_user: User,
        db: Session
    ) -> Activity:
        """Update activity"""
        activity = ActivityController.get_activity(activity_id, company_id, current_user, db)
        
        # Store old customer_id before update
        old_customer_id = activity.customer_id
        
        update_data = activity_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(activity, key, value)
        
        db.commit()
        db.refresh(activity)
        
        # Auto-update health score for both old and new customer (if changed)
        if activity.customer_id or old_customer_id:
            from app.utils.health_score import HealthScoreCalculator
            if activity.customer_id:
                HealthScoreCalculator.update_health_score(
                    activity.customer_id,
                    company_id,
                    db,
                    force_update=True
                )
            if old_customer_id and old_customer_id != activity.customer_id:
                HealthScoreCalculator.update_health_score(
                    old_customer_id,
                    company_id,
                    db,
                    force_update=True
                )
        
        return activity
    
    @staticmethod
    def delete_activity(
        activity_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ):
        """Delete activity"""
        activity = db.query(Activity).filter(
            Activity.id == activity_id,
            Activity.company_id == company_id
        ).first()
        
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        
        # Store customer_id before deletion
        customer_id = activity.customer_id
        
        db.delete(activity)
        db.commit()
        
        # Auto-update customer health score after deletion
        if customer_id:
            from app.utils.health_score import HealthScoreCalculator
            HealthScoreCalculator.update_health_score(
                customer_id,
                company_id,
                db,
                force_update=True
            )
    
    @staticmethod
    def get_timeline(
        company_id: int,
        current_user: User,
        db: Session,
        customer_id: Optional[int] = None,
        lead_id: Optional[int] = None,
        deal_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Activity]:
        """Get activity timeline"""
        query = db.query(Activity).filter(Activity.company_id == company_id)
        
        if customer_id:
            query = query.filter(Activity.customer_id == customer_id)
        
        if lead_id:
            query = query.filter(Activity.lead_id == lead_id)
        
        if deal_id:
            query = query.filter(Activity.deal_id == deal_id)
        
        activities = query.order_by(Activity.activity_date.desc()).limit(limit).all()
        return activities

