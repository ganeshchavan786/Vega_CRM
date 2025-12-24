"""
BANT/MEDDICC Qualification Scoring
Calculates qualification score and risk level
"""

from typing import Dict, Optional
from app.models.lead import Lead


class QualificationScoring:
    """BANT/MEDDICC qualification scoring"""
    
    @staticmethod
    def calculate_bant_score(lead: Lead) -> Dict:
        """
        Calculate BANT qualification score
        
        BANT Criteria:
        - Budget: Available budget for purchase
        - Authority: Decision-making authority
        - Need: Business need/pain point
        - Timeline: Purchase timeline
        
        Args:
            lead: Lead object
            
        Returns:
            Dictionary with BANT score and details
        """
        score = 0
        max_score = 4
        criteria_met = []
        criteria_missing = []
        
        # Budget (1 point)
        if hasattr(lead, 'budget_range') and lead.budget_range and lead.budget_range.lower() not in ['not disclosed', 'n/a', 'none', '']:
            score += 1
            criteria_met.append("Budget")
        else:
            criteria_missing.append("Budget")
        
        # Authority (1 point)
        if hasattr(lead, 'authority_level') and lead.authority_level:
            authority = lead.authority_level.lower()
            if authority in ['decision_maker', 'economic_buyer']:
                score += 1
                criteria_met.append("Authority")
            elif authority in ['influencer', 'champion']:
                score += 0.5  # Partial credit
                criteria_met.append("Authority (Partial)")
            else:
                criteria_missing.append("Authority")
        else:
            criteria_missing.append("Authority")
        
        # Need (1 point)
        if hasattr(lead, 'interest_product') and lead.interest_product and lead.interest_product.strip():
            score += 1
            criteria_met.append("Need")
        else:
            criteria_missing.append("Need")
        
        # Timeline (1 point)
        if hasattr(lead, 'timeline') and lead.timeline and lead.timeline.lower() not in ['not disclosed', 'n/a', 'none', '']:
            score += 1
            criteria_met.append("Timeline")
        else:
            criteria_missing.append("Timeline")
        
        percentage = (score / max_score) * 100
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "criteria_met": criteria_met,
            "criteria_missing": criteria_missing,
            "is_qualified": score >= 3  # 3/4 criteria met = qualified
        }
    
    @staticmethod
    def calculate_meddicc_score(lead: Lead) -> Dict:
        """
        Calculate MEDDICC qualification score (extended framework)
        
        MEDDICC Criteria:
        - Metrics: Business metrics/ROI
        - Economic Buyer: Person with budget authority
        - Decision Criteria: Evaluation criteria
        - Decision Process: How decisions are made
        - Identify Pain: Current pain points
        - Champion: Internal advocate
        - Competition: Competing solutions
        
        Args:
            lead: Lead object
            
        Returns:
            Dictionary with MEDDICC score and details
        """
        score = 0
        max_score = 7
        criteria_met = []
        criteria_missing = []
        
        # Metrics (1 point) - Not directly in lead model, check notes
        if hasattr(lead, 'notes') and lead.notes:
            notes_lower = lead.notes.lower()
            if any(keyword in notes_lower for keyword in ['roi', 'efficiency', 'metrics', 'kpi', 'performance']):
                score += 1
                criteria_met.append("Metrics")
            else:
                criteria_missing.append("Metrics")
        else:
            criteria_missing.append("Metrics")
        
        # Economic Buyer (1 point)
        if hasattr(lead, 'authority_level') and lead.authority_level:
            authority = lead.authority_level.lower()
            if authority in ['decision_maker', 'economic_buyer']:
                score += 1
                criteria_met.append("Economic Buyer")
            else:
                criteria_missing.append("Economic Buyer")
        else:
            criteria_missing.append("Economic Buyer")
        
        # Decision Criteria (1 point) - Check notes or interest_product
        if hasattr(lead, 'interest_product') and lead.interest_product:
            score += 1
            criteria_met.append("Decision Criteria")
        else:
            criteria_missing.append("Decision Criteria")
        
        # Decision Process (1 point) - Check notes
        if hasattr(lead, 'notes') and lead.notes:
            notes_lower = lead.notes.lower()
            if any(keyword in notes_lower for keyword in ['process', 'approval', 'committee', 'decision']):
                score += 1
                criteria_met.append("Decision Process")
            else:
                criteria_missing.append("Decision Process")
        else:
            criteria_missing.append("Decision Process")
        
        # Identify Pain (1 point) - Check notes
        if hasattr(lead, 'notes') and lead.notes:
            notes_lower = lead.notes.lower()
            if any(keyword in notes_lower for keyword in ['pain', 'problem', 'issue', 'challenge', 'difficulty']):
                score += 1
                criteria_met.append("Identify Pain")
            else:
                criteria_missing.append("Identify Pain")
        else:
            criteria_missing.append("Identify Pain")
        
        # Champion (1 point) - Authority level influencer/champion
        if hasattr(lead, 'authority_level') and lead.authority_level:
            authority = lead.authority_level.lower()
            if authority in ['influencer', 'champion']:
                score += 1
                criteria_met.append("Champion")
            else:
                criteria_missing.append("Champion")
        else:
            criteria_missing.append("Champion")
        
        # Competition (1 point) - Check notes
        if hasattr(lead, 'notes') and lead.notes:
            notes_lower = lead.notes.lower()
            if any(keyword in notes_lower for keyword in ['competitor', 'alternative', 'other solution', 'comparing']):
                score += 1
                criteria_met.append("Competition")
            else:
                criteria_missing.append("Competition")
        else:
            criteria_missing.append("Competition")
        
        percentage = (score / max_score) * 100
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "criteria_met": criteria_met,
            "criteria_missing": criteria_missing,
            "is_qualified": score >= 5  # 5/7 criteria met = qualified
        }
    
    @staticmethod
    def calculate_risk_score(lead: Lead) -> Dict:
        """
        Calculate risk score based on BANT/MEDDICC
        
        Risk Levels:
        - Low Risk: All BANT criteria met, high authority
        - Medium Risk: 3/4 BANT criteria met, medium authority
        - High Risk: <3 BANT criteria met, low authority
        
        Args:
            lead: Lead object
            
        Returns:
            Dictionary with risk score and level
        """
        bant_score = QualificationScoring.calculate_bant_score(lead)
        
        # Get authority level
        authority_level = "low"
        if hasattr(lead, 'authority_level') and lead.authority_level:
            authority = lead.authority_level.lower()
            if authority in ['decision_maker', 'economic_buyer']:
                authority_level = "high"
            elif authority in ['influencer', 'champion']:
                authority_level = "medium"
            else:
                authority_level = "low"
        
        # Determine risk level
        bant_count = bant_score["score"]
        
        if bant_count == 4 and authority_level == "high":
            risk_level = "low"
            risk_score = 1
        elif bant_count >= 3 and authority_level in ["high", "medium"]:
            risk_level = "medium"
            risk_score = 2
        else:
            risk_level = "high"
            risk_score = 3
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "bant_score": bant_count,
            "authority_level": authority_level,
            "reason": f"BANT: {bant_count}/4, Authority: {authority_level}"
        }
    
    @staticmethod
    def get_qualification_summary(lead: Lead) -> Dict:
        """
        Get complete qualification summary (BANT + MEDDICC + Risk)
        
        Args:
            lead: Lead object
            
        Returns:
            Dictionary with complete qualification summary
        """
        bant = QualificationScoring.calculate_bant_score(lead)
        meddicc = QualificationScoring.calculate_meddicc_score(lead)
        risk = QualificationScoring.calculate_risk_score(lead)
        
        # Overall qualification status
        is_qualified = bant["is_qualified"] or meddicc["is_qualified"]
        
        return {
            "is_qualified": is_qualified,
            "bant": bant,
            "meddicc": meddicc,
            "risk": risk,
            "recommendation": "Qualified - Ready for conversion" if is_qualified else "Needs more qualification"
        }

