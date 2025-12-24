"""
Account Health Score Calculator
Automatically calculates health score based on engagement, activities, and deals
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional
from app.models.customer import Customer
from app.models.activity import Activity
from app.models.deal import Deal


class HealthScoreCalculator:
    """Calculate account health score based on engagement metrics"""
    
    # Health Score Thresholds
    GREEN_THRESHOLD = 70  # 70+ points = Green
    YELLOW_THRESHOLD = 40  # 40-69 points = Yellow
    RED_THRESHOLD = 20    # 20-39 points = Red
    # Below 20 = Black
    
    @staticmethod
    def calculate_health_score(
        customer: Customer,
        db: Session,
        days_lookback: int = 90
    ) -> str:
        """
        Calculate health score for a customer account
        
        Scoring factors:
        1. Recent activities (last 30/60/90 days) - 40 points max
        2. Deal pipeline status - 30 points max
        3. Last interaction recency - 20 points max
        4. Account status - 10 points max
        
        Args:
            customer: Customer/Account object
            db: Database session
            days_lookback: Number of days to look back for activities
            
        Returns:
            Health score: 'green', 'yellow', 'red', or 'black'
        """
        score = 0
        max_score = 100
        
        # 1. Recent Activities Score (40 points max)
        activity_score = HealthScoreCalculator._calculate_activity_score(
            customer, db, days_lookback
        )
        score += activity_score
        
        # 2. Deal Pipeline Score (30 points max)
        deal_score = HealthScoreCalculator._calculate_deal_score(customer, db)
        score += deal_score
        
        # 3. Last Interaction Recency Score (20 points max)
        recency_score = HealthScoreCalculator._calculate_recency_score(
            customer, db
        )
        score += recency_score
        
        # 4. Account Status Score (10 points max)
        status_score = HealthScoreCalculator._calculate_status_score(customer)
        score += status_score
        
        # Determine health score category
        if score >= HealthScoreCalculator.GREEN_THRESHOLD:
            return "green"
        elif score >= HealthScoreCalculator.YELLOW_THRESHOLD:
            return "yellow"
        elif score >= HealthScoreCalculator.RED_THRESHOLD:
            return "red"
        else:
            return "black"
    
    @staticmethod
    def _calculate_activity_score(
        customer: Customer,
        db: Session,
        days_lookback: int
    ) -> int:
        """
        Calculate score based on recent activities
        
        Scoring:
        - Activities in last 30 days: 5 points each (max 20 points)
        - Activities in last 31-60 days: 3 points each (max 12 points)
        - Activities in last 61-90 days: 2 points each (max 8 points)
        - Positive outcomes: +2 bonus per activity
        - Total max: 40 points
        """
        score = 0
        now = datetime.now()
        
        # Get activities in last 90 days
        cutoff_date = now - timedelta(days=days_lookback)
        activities = db.query(Activity).filter(
            and_(
                Activity.customer_id == customer.id,
                Activity.company_id == customer.company_id,
                Activity.activity_date >= cutoff_date
            )
        ).order_by(Activity.activity_date.desc()).all()
        
        for activity in activities:
            days_ago = (now - activity.activity_date).days
            
            if days_ago <= 30:
                score += 5
            elif days_ago <= 60:
                score += 3
            elif days_ago <= 90:
                score += 2
            
            # Bonus for positive outcomes
            if activity.outcome == "positive":
                score += 2
        
        return min(score, 40)  # Cap at 40 points
    
    @staticmethod
    def _calculate_deal_score(customer: Customer, db: Session) -> int:
        """
        Calculate score based on deal pipeline
        
        Scoring:
        - Open deals: 5 points each (max 15 points)
        - Won deals in last 90 days: 10 points each (max 10 points)
        - Deal value multiplier: +1 point per ₹1L (max 5 points)
        - Total max: 30 points
        """
        score = 0
        now = datetime.now()
        cutoff_date = now - timedelta(days=90)
        
        # Get all deals for this customer
        deals = db.query(Deal).filter(
            and_(
                or_(
                    Deal.customer_id == customer.id,
                    Deal.account_id == customer.id
                ),
                Deal.company_id == customer.company_id
            )
        ).all()
        
        open_deals = [d for d in deals if d.status == "open"]
        won_deals = [
            d for d in deals 
            if d.status == "won" and d.actual_close_date and d.actual_close_date >= cutoff_date.date()
        ]
        
        # Open deals score (max 15)
        score += min(len(open_deals) * 5, 15)
        
        # Won deals score (max 10)
        score += min(len(won_deals) * 10, 10)
        
        # Deal value score (max 5)
        total_deal_value = sum(
            float(d.deal_value or 0) for d in open_deals + won_deals
        )
        # Convert to lakhs (divide by 100000) and cap at 5
        value_score = min(int(total_deal_value / 100000), 5)
        score += value_score
        
        return min(score, 30)  # Cap at 30 points
    
    @staticmethod
    def _calculate_recency_score(customer: Customer, db: Session) -> int:
        """
        Calculate score based on last interaction recency
        
        Scoring:
        - Last 7 days: 20 points
        - Last 8-30 days: 15 points
        - Last 31-60 days: 10 points
        - Last 61-90 days: 5 points
        - Over 90 days: 0 points
        - No activities: 0 points
        """
        # Get most recent activity
        last_activity = db.query(Activity).filter(
            and_(
                Activity.customer_id == customer.id,
                Activity.company_id == customer.company_id
            )
        ).order_by(Activity.activity_date.desc()).first()
        
        if not last_activity:
            return 0
        
        days_ago = (datetime.now() - last_activity.activity_date).days
        
        if days_ago <= 7:
            return 20
        elif days_ago <= 30:
            return 15
        elif days_ago <= 60:
            return 10
        elif days_ago <= 90:
            return 5
        else:
            return 0
    
    @staticmethod
    def _calculate_status_score(customer: Customer) -> int:
        """
        Calculate score based on account status
        
        Scoring:
        - Active: 10 points
        - Prospect: 5 points
        - Inactive: 0 points
        - Lost: 0 points
        """
        if customer.status == "active":
            return 10
        elif customer.status == "prospect":
            return 5
        else:
            return 0
    
    @staticmethod
    def update_health_score(
        customer_id: int,
        company_id: int,
        db: Session,
        force_update: bool = False
    ) -> Optional[str]:
        """
        Update health score for a customer
        
        Args:
            customer_id: Customer ID
            company_id: Company ID
            db: Database session
            force_update: Force update even if recently calculated
            
        Returns:
            New health score or None if not updated
        """
        customer = db.query(Customer).filter(
            and_(
                Customer.id == customer_id,
                Customer.company_id == company_id
            )
        ).first()
        
        if not customer:
            return None
        
        # Calculate new health score
        new_score = HealthScoreCalculator.calculate_health_score(customer, db)
        
        # Update if different or forced
        if force_update or customer.health_score != new_score:
            customer.health_score = new_score
            db.commit()
            return new_score
        
        return customer.health_score
    
    @staticmethod
    def batch_update_health_scores(
        company_id: int,
        db: Session,
        customer_ids: Optional[list] = None
    ) -> dict:
        """
        Batch update health scores for multiple customers
        
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
            old_score = customer.health_score
            new_score = HealthScoreCalculator.calculate_health_score(customer, db)
            
            if old_score != new_score:
                customer.health_score = new_score
                updated += 1
            else:
                unchanged += 1
        
        db.commit()
        
        return {
            "total": len(customers),
            "updated": updated,
            "unchanged": unchanged
        }

