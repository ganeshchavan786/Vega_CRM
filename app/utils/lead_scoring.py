"""
Lead Scoring Algorithm
ML-based lead scoring (0-100) with automatic score calculation and increment
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from app.models.lead import Lead
from app.models.activity import Activity


class LeadScoringAlgorithm:
    """Calculate and update lead scores based on engagement and qualification"""
    
    # Score Ranges
    MIN_SCORE = 0
    MAX_SCORE = 100
    
    # Score Thresholds
    HIGH_SCORE_THRESHOLD = 70  # High priority leads
    MEDIUM_SCORE_THRESHOLD = 40  # Medium priority leads
    LOW_SCORE_THRESHOLD = 20  # Low priority leads
    
    @staticmethod
    def calculate_lead_score(
        lead: Lead,
        db: Session
    ) -> int:
        """
        Calculate comprehensive lead score (0-100)
        
        Scoring factors:
        1. Source Quality (20 points max)
        2. Qualification Fields - BANT (30 points max)
        3. Engagement Activities (30 points max)
        4. Data Completeness (10 points max)
        5. Authority & Priority (10 points max)
        
        Args:
            lead: Lead object
            db: Database session
            
        Returns:
            Lead score (0-100)
        """
        score = 0
        
        # 1. Source Quality Score (20 points max)
        source_score = LeadScoringAlgorithm._calculate_source_score(lead)
        score += source_score
        
        # 2. Qualification Fields - BANT Score (30 points max)
        bant_score = LeadScoringAlgorithm._calculate_bant_score(lead)
        score += bant_score
        
        # 3. Engagement Activities Score (30 points max)
        engagement_score = LeadScoringAlgorithm._calculate_engagement_score(lead, db)
        score += engagement_score
        
        # 4. Data Completeness Score (10 points max)
        completeness_score = LeadScoringAlgorithm._calculate_completeness_score(lead)
        score += completeness_score
        
        # 5. Authority & Priority Score (10 points max)
        authority_score = LeadScoringAlgorithm._calculate_authority_score(lead)
        score += authority_score
        
        # Ensure score is within bounds
        return max(LeadScoringAlgorithm.MIN_SCORE, min(score, LeadScoringAlgorithm.MAX_SCORE))
    
    @staticmethod
    def _calculate_source_score(lead: Lead) -> int:
        """
        Calculate score based on lead source quality
        
        Scoring:
        - High-quality sources (Website, Referral, Partner): 15-20 points
        - Medium-quality sources (Google Ads, Social): 10-15 points
        - Low-quality sources (Cold Call, Manual): 5-10 points
        - Missing source: 0 points
        """
        if not lead.source:
            return 0
        
        source_lower = lead.source.lower()
        
        # High-quality sources
        if any(keyword in source_lower for keyword in ['website', 'referral', 'partner', 'event', 'webinar']):
            return 20
        # Medium-quality sources
        elif any(keyword in source_lower for keyword in ['google', 'ads', 'social', 'facebook', 'linkedin', 'email']):
            return 15
        # Low-quality sources
        elif any(keyword in source_lower for keyword in ['cold', 'manual', 'import', 'csv']):
            return 5
        else:
            return 10  # Default medium score
    
    @staticmethod
    def _calculate_bant_score(lead: Lead) -> int:
        """
        Calculate score based on BANT qualification fields
        
        Scoring:
        - Budget Range: 10 points if provided
        - Authority Level: 10 points (Decision Maker: 10, Influencer: 7, User: 5)
        - Timeline: 5 points if provided and reasonable (< 6 months)
        - Interest Product: 5 points if provided
        """
        score = 0
        
        # Budget Range (10 points)
        if lead.budget_range and lead.budget_range.lower() not in ['not disclosed', 'unknown', '']:
            score += 10
        
        # Authority Level (10 points)
        if lead.authority_level:
            auth_lower = lead.authority_level.lower()
            if 'decision' in auth_lower or 'maker' in auth_lower:
                score += 10
            elif 'influencer' in auth_lower:
                score += 7
            elif 'user' in auth_lower:
                score += 5
            else:
                score += 3
        
        # Timeline (5 points)
        if lead.timeline:
            timeline_lower = lead.timeline.lower()
            # Quick timeline is better
            if any(keyword in timeline_lower for keyword in ['30', '60', '90', 'immediate', 'urgent', 'soon']):
                score += 5
            elif any(keyword in timeline_lower for keyword in ['3', '6', 'month']):
                score += 3
            else:
                score += 1
        
        # Interest Product (5 points)
        if lead.interest_product and lead.interest_product.strip():
            score += 5
        
        return min(score, 30)  # Cap at 30 points
    
    @staticmethod
    def _calculate_engagement_score(lead: Lead, db: Session) -> int:
        """
        Calculate score based on engagement activities
        
        Scoring:
        - Activities in last 7 days: 10 points each (max 20)
        - Activities in last 8-30 days: 5 points each (max 10)
        - Positive outcomes: +3 bonus per activity
        - Email opens: +5 points each (tracked via activities)
        - Email clicks: +10 points each (tracked via activities)
        - Total max: 30 points
        """
        score = 0
        now = datetime.now()
        
        # Get activities in last 30 days
        cutoff_date = now - timedelta(days=30)
        activities = db.query(Activity).filter(
            and_(
                Activity.lead_id == lead.id,
                Activity.company_id == lead.company_id,
                Activity.activity_date >= cutoff_date
            )
        ).order_by(Activity.activity_date.desc()).all()
        
        for activity in activities:
            days_ago = (now - activity.activity_date).days
            
            if days_ago <= 7:
                score += 10
            elif days_ago <= 30:
                score += 5
            
            # Bonus for positive outcomes
            if activity.outcome == "positive":
                score += 3
            
            # Email engagement (tracked via activity type and description)
            if activity.activity_type == "email":
                if "opened" in (activity.description or "").lower():
                    score += 5
                if "clicked" in (activity.description or "").lower():
                    score += 10
        
        return min(score, 30)  # Cap at 30 points
    
    @staticmethod
    def _calculate_completeness_score(lead: Lead) -> int:
        """
        Calculate score based on data completeness
        
        Scoring:
        - Email: 2 points
        - Phone: 2 points
        - Company Name: 2 points
        - First Name + Last Name: 2 points
        - Source Attribution (Source, Campaign, Medium, Term): 2 points
        - Total max: 10 points
        """
        score = 0
        
        if lead.email and lead.email.strip():
            score += 2
        
        if lead.phone and lead.phone.strip():
            score += 2
        
        if lead.company_name and lead.company_name.strip():
            score += 2
        
        if lead.first_name and lead.last_name:
            score += 2
        
        # Source attribution completeness
        if lead.source and lead.campaign and lead.medium:
            score += 2
        
        return min(score, 10)  # Cap at 10 points
    
    @staticmethod
    def _calculate_authority_score(lead: Lead) -> int:
        """
        Calculate score based on authority level and priority
        
        Scoring:
        - Priority: High (5 points), Medium (3 points), Low (1 point)
        - Authority Level: Already counted in BANT, but add bonus here
        - Total max: 10 points
        """
        score = 0
        
        # Priority score
        if lead.priority:
            priority_lower = lead.priority.lower()
            if priority_lower == "high":
                score += 5
            elif priority_lower == "medium":
                score += 3
            else:
                score += 1
        
        # Authority bonus (if not already counted)
        if lead.authority_level:
            auth_lower = lead.authority_level.lower()
            if 'decision' in auth_lower or 'maker' in auth_lower:
                score += 5
            elif 'influencer' in auth_lower:
                score += 3
        
        return min(score, 10)  # Cap at 10 points
    
    @staticmethod
    def increment_lead_score(
        lead_id: int,
        company_id: int,
        increment: int,
        db: Session,
        reason: Optional[str] = None
    ) -> Optional[int]:
        """
        Increment lead score by a specific amount
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            increment: Points to add (can be negative)
            reason: Reason for increment (for logging)
            
        Returns:
            New lead score or None if lead not found
        """
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            return None
        
        # Get current score or calculate if None
        current_score = lead.lead_score if lead.lead_score is not None else 0
        
        # Increment score
        new_score = current_score + increment
        
        # Ensure score is within bounds
        new_score = max(LeadScoringAlgorithm.MIN_SCORE, min(new_score, LeadScoringAlgorithm.MAX_SCORE))
        
        lead.lead_score = new_score
        db.commit()
        
        # Log score increment (optional)
        if reason:
            LeadScoringAlgorithm._log_score_increment(lead, increment, new_score, reason, db)
        
        return new_score
    
    @staticmethod
    def _log_score_increment(
        lead: Lead,
        increment: int,
        new_score: int,
        reason: str,
        db: Session
    ):
        """
        Log lead score increment as an activity
        
        Args:
            lead: Lead object
            increment: Score increment amount
            new_score: New total score
            reason: Reason for increment
            db: Database session
        """
        try:
            activity = Activity(
                company_id=lead.company_id,
                lead_id=lead.id,
                activity_type="note",
                title=f"Lead Score Updated: {increment:+d} points",
                description=f"Lead score incremented by {increment} points. New score: {new_score}/100. Reason: {reason}",
                user_id=lead.lead_owner_id or lead.assigned_to or lead.created_by,
                activity_date=datetime.now()
            )
            
            db.add(activity)
            db.commit()
        except Exception as e:
            # Don't fail if logging fails
            print(f"Error logging lead score increment: {e}")
            pass
    
    @staticmethod
    def update_lead_score(
        lead_id: int,
        company_id: int,
        db: Session,
        force_update: bool = False
    ) -> Optional[int]:
        """
        Recalculate and update lead score
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            force_update: Force update even if recently calculated
            
        Returns:
            New lead score or None if lead not found
        """
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            return None
        
        # Calculate new score
        new_score = LeadScoringAlgorithm.calculate_lead_score(lead, db)
        
        # Update if different or forced
        if force_update or lead.lead_score != new_score:
            old_score = lead.lead_score
            lead.lead_score = new_score
            db.commit()
            
            # Log score change if significant
            if old_score is not None and abs(new_score - old_score) >= 5:
                LeadScoringAlgorithm._log_score_increment(
                    lead,
                    new_score - (old_score or 0),
                    new_score,
                    "Automatic recalculation",
                    db
                )
            
            return new_score
        
        return lead.lead_score
    
    @staticmethod
    def batch_update_lead_scores(
        company_id: int,
        db: Session,
        lead_ids: Optional[list] = None
    ) -> dict:
        """
        Batch update lead scores for multiple leads
        
        Args:
            company_id: Company ID
            db: Database session
            lead_ids: Optional list of lead IDs to update (None = all)
            
        Returns:
            Dictionary with update statistics
        """
        query = db.query(Lead).filter(Lead.company_id == company_id)
        
        if lead_ids:
            query = query.filter(Lead.id.in_(lead_ids))
        
        leads = query.all()
        
        updated = 0
        unchanged = 0
        
        for lead in leads:
            old_score = lead.lead_score
            new_score = LeadScoringAlgorithm.calculate_lead_score(lead, db)
            
            if old_score != new_score:
                lead.lead_score = new_score
                updated += 1
            else:
                unchanged += 1
        
        db.commit()
        
        return {
            "total": len(leads),
            "updated": updated,
            "unchanged": unchanged
        }
    
    @staticmethod
    def get_score_category(score: int) -> str:
        """
        Get score category based on score value
        
        Args:
            score: Lead score (0-100)
            
        Returns:
            Category: 'high', 'medium', 'low', or 'very_low'
        """
        if score >= LeadScoringAlgorithm.HIGH_SCORE_THRESHOLD:
            return "high"
        elif score >= LeadScoringAlgorithm.MEDIUM_SCORE_THRESHOLD:
            return "medium"
        elif score >= LeadScoringAlgorithm.LOW_SCORE_THRESHOLD:
            return "low"
        else:
            return "very_low"
    
    @staticmethod
    def can_convert(lead: Lead) -> bool:
        """
        Check if lead can be converted based on score and status
        
        Rule: Lead Score > 70 AND Status = "Contacted"
        
        Args:
            lead: Lead object
            
        Returns:
            True if can convert, False otherwise
        """
        if not lead.lead_score:
            return False
        
        return (
            lead.lead_score >= LeadScoringAlgorithm.HIGH_SCORE_THRESHOLD and
            lead.status == "contacted"
        )

