"""
Risk Scoring Service
Calculates and manages lead risk scores based on BANT criteria and other factors
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.activity import Activity


class RiskScoringService:
    """Service for lead risk scoring and assessment"""
    
    # Risk Levels
    LOW_RISK = "low"
    MEDIUM_RISK = "medium"
    HIGH_RISK = "high"
    CRITICAL_RISK = "critical"
    
    # Risk Thresholds (lower score = higher risk)
    LOW_RISK_THRESHOLD = 70  # Score >= 70 = Low Risk
    MEDIUM_RISK_THRESHOLD = 50  # Score 50-69 = Medium Risk
    HIGH_RISK_THRESHOLD = 30  # Score 30-49 = High Risk
    # Score < 30 = Critical Risk
    
    @staticmethod
    def calculate_risk_score(lead: Lead, db: Session) -> Dict:
        """
        Calculate risk score for a lead (0-100, higher = better/lower risk)
        
        Risk Factors:
        1. BANT Completion (40 points)
        2. Engagement Level (25 points)
        3. Data Quality (20 points)
        4. Time Factors (15 points)
        
        Args:
            lead: Lead object
            db: Database session
            
        Returns:
            Risk assessment dictionary
        """
        scores = {
            "bant_completion": 0,
            "engagement": 0,
            "data_quality": 0,
            "time_factors": 0
        }
        risk_factors = []
        
        # 1. BANT Completion Score (40 points)
        bant_items = 0
        if lead.budget_range and lead.budget_range.lower() not in ["not disclosed", "unknown", ""]:
            bant_items += 1
        else:
            risk_factors.append("Missing budget information")
        
        if lead.authority_level:
            bant_items += 1
            if "decision" in lead.authority_level.lower() or "maker" in lead.authority_level.lower():
                scores["bant_completion"] += 5  # Bonus for decision maker
        else:
            risk_factors.append("Authority level not identified")
        
        if lead.interest_product and lead.interest_product.strip():
            bant_items += 1
        else:
            risk_factors.append("No specific need/product interest")
        
        if lead.timeline:
            bant_items += 1
        else:
            risk_factors.append("No timeline specified")
        
        scores["bant_completion"] += (bant_items / 4) * 35  # Up to 35 + 5 bonus = 40
        
        # 2. Engagement Level (25 points)
        recent_activities = db.query(func.count(Activity.id)).filter(
            Activity.lead_id == lead.id,
            Activity.activity_date >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        if recent_activities >= 5:
            scores["engagement"] = 25
        elif recent_activities >= 3:
            scores["engagement"] = 20
        elif recent_activities >= 1:
            scores["engagement"] = 15
        else:
            scores["engagement"] = 5
            risk_factors.append("Low engagement in last 30 days")
        
        # 3. Data Quality (20 points)
        data_points = 0
        if lead.email and "@" in lead.email:
            data_points += 1
        else:
            risk_factors.append("Missing or invalid email")
        
        if lead.phone and len(lead.phone) >= 10:
            data_points += 1
        else:
            risk_factors.append("Missing or invalid phone")
        
        if lead.company_name:
            data_points += 1
        
        if lead.first_name and lead.last_name:
            data_points += 1
        
        scores["data_quality"] = (data_points / 4) * 20
        
        # 4. Time Factors (15 points)
        days_since_creation = (datetime.utcnow() - lead.created_at).days if lead.created_at else 0
        days_since_update = (datetime.utcnow() - lead.updated_at).days if lead.updated_at else days_since_creation
        
        # Newer leads with recent activity are lower risk
        if days_since_update <= 7:
            scores["time_factors"] = 15
        elif days_since_update <= 14:
            scores["time_factors"] = 12
        elif days_since_update <= 30:
            scores["time_factors"] = 8
        else:
            scores["time_factors"] = 3
            risk_factors.append(f"No activity in {days_since_update} days")
        
        # Calculate total score
        total_score = sum(scores.values())
        
        # Determine risk level
        if total_score >= RiskScoringService.LOW_RISK_THRESHOLD:
            risk_level = RiskScoringService.LOW_RISK
        elif total_score >= RiskScoringService.MEDIUM_RISK_THRESHOLD:
            risk_level = RiskScoringService.MEDIUM_RISK
        elif total_score >= RiskScoringService.HIGH_RISK_THRESHOLD:
            risk_level = RiskScoringService.HIGH_RISK
        else:
            risk_level = RiskScoringService.CRITICAL_RISK
        
        return {
            "total_score": round(total_score, 2),
            "max_score": 100,
            "risk_level": risk_level,
            "breakdown": {k: round(v, 2) for k, v in scores.items()},
            "risk_factors": risk_factors,
            "recommendations": RiskScoringService._get_recommendations(risk_level, risk_factors)
        }
    
    @staticmethod
    def _get_recommendations(risk_level: str, risk_factors: List[str]) -> List[str]:
        """Get recommendations based on risk level and factors"""
        recommendations = []
        
        if "Missing budget information" in risk_factors:
            recommendations.append("Schedule discovery call to understand budget")
        
        if "Authority level not identified" in risk_factors:
            recommendations.append("Identify decision maker in the organization")
        
        if "No specific need/product interest" in risk_factors:
            recommendations.append("Conduct needs assessment call")
        
        if "No timeline specified" in risk_factors:
            recommendations.append("Establish project timeline and urgency")
        
        if "Low engagement in last 30 days" in risk_factors:
            recommendations.append("Re-engage with personalized outreach")
        
        if risk_level == RiskScoringService.CRITICAL_RISK:
            recommendations.append("Consider disqualifying or archiving this lead")
        elif risk_level == RiskScoringService.HIGH_RISK:
            recommendations.append("Prioritize immediate follow-up")
        
        return recommendations
    
    @staticmethod
    def update_lead_risk_score(
        lead_id: int,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Update risk score for a lead
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            
        Returns:
            Updated risk assessment
        """
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            return {"success": False, "error": "Lead not found"}
        
        risk_result = RiskScoringService.calculate_risk_score(lead, db)
        
        return {
            "success": True,
            "lead_id": lead_id,
            "lead_name": lead.lead_name,
            "risk_assessment": risk_result
        }
    
    @staticmethod
    def get_high_risk_leads(company_id: int, db: Session) -> List[Dict]:
        """
        Get all high and critical risk leads
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            List of high risk leads
        """
        leads = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status.notin_(["converted", "disqualified"])
        ).all()
        
        high_risk_leads = []
        for lead in leads:
            risk_result = RiskScoringService.calculate_risk_score(lead, db)
            if risk_result["risk_level"] in [RiskScoringService.HIGH_RISK, RiskScoringService.CRITICAL_RISK]:
                high_risk_leads.append({
                    "lead_id": lead.id,
                    "lead_name": lead.lead_name,
                    "email": lead.email,
                    "risk_score": risk_result["total_score"],
                    "risk_level": risk_result["risk_level"],
                    "risk_factors": risk_result["risk_factors"],
                    "recommendations": risk_result["recommendations"]
                })
        
        # Sort by risk score (lowest first = highest risk)
        high_risk_leads.sort(key=lambda x: x["risk_score"])
        
        return high_risk_leads
    
    @staticmethod
    def get_risk_analytics(company_id: int, db: Session) -> Dict:
        """
        Get risk analytics for a company
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Risk analytics
        """
        leads = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status.notin_(["converted", "disqualified"])
        ).all()
        
        risk_distribution = {
            RiskScoringService.LOW_RISK: 0,
            RiskScoringService.MEDIUM_RISK: 0,
            RiskScoringService.HIGH_RISK: 0,
            RiskScoringService.CRITICAL_RISK: 0
        }
        
        total_score = 0
        for lead in leads:
            risk_result = RiskScoringService.calculate_risk_score(lead, db)
            risk_distribution[risk_result["risk_level"]] += 1
            total_score += risk_result["total_score"]
        
        total_leads = len(leads)
        avg_score = round(total_score / total_leads, 2) if total_leads > 0 else 0
        
        return {
            "total_leads": total_leads,
            "average_risk_score": avg_score,
            "risk_distribution": risk_distribution,
            "high_risk_count": risk_distribution[RiskScoringService.HIGH_RISK] + risk_distribution[RiskScoringService.CRITICAL_RISK],
            "risk_percentage": {
                level: round((count / total_leads * 100), 2) if total_leads > 0 else 0
                for level, count in risk_distribution.items()
            }
        }
    
    @staticmethod
    def batch_update_risk_scores(
        company_id: int,
        db: Session,
        lead_ids: Optional[List[int]] = None
    ) -> Dict:
        """
        Batch update risk scores for multiple leads
        
        Args:
            company_id: Company ID
            db: Database session
            lead_ids: Optional list of lead IDs
            
        Returns:
            Batch update results
        """
        query = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status.notin_(["converted", "disqualified"])
        )
        
        if lead_ids:
            query = query.filter(Lead.id.in_(lead_ids))
        
        leads = query.all()
        
        results = {
            "total": len(leads),
            "by_risk_level": {
                RiskScoringService.LOW_RISK: 0,
                RiskScoringService.MEDIUM_RISK: 0,
                RiskScoringService.HIGH_RISK: 0,
                RiskScoringService.CRITICAL_RISK: 0
            }
        }
        
        for lead in leads:
            risk_result = RiskScoringService.calculate_risk_score(lead, db)
            results["by_risk_level"][risk_result["risk_level"]] += 1
        
        return results
