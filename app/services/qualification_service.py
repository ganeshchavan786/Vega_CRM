"""
Lead Qualification Service
Handles BANT/MEDDICC qualification scoring, workflow, and status management
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.activity import Activity


class QualificationService:
    """Service for lead qualification using BANT/MEDDICC framework"""
    
    # BANT Weights (Total: 100)
    BUDGET_WEIGHT = 25
    AUTHORITY_WEIGHT = 30
    NEED_WEIGHT = 25
    TIMELINE_WEIGHT = 20
    
    # Qualification Thresholds
    QUALIFIED_THRESHOLD = 70
    PARTIALLY_QUALIFIED_THRESHOLD = 40
    
    @staticmethod
    def calculate_bant_score(lead: Lead) -> Dict:
        """
        Calculate BANT qualification score (0-100)
        
        Args:
            lead: Lead object
            
        Returns:
            Dictionary with score breakdown
        """
        scores = {
            "budget": 0,
            "authority": 0,
            "need": 0,
            "timeline": 0
        }
        
        # Budget Score (25 points)
        if lead.budget_range:
            budget = lead.budget_range.lower()
            if any(x in budget for x in ["100k", "500k", "1m", "million", "lakh", "crore"]):
                scores["budget"] = 25
            elif any(x in budget for x in ["50k", "75k", "enterprise"]):
                scores["budget"] = 20
            elif any(x in budget for x in ["10k", "25k", "medium"]):
                scores["budget"] = 15
            elif budget not in ["not disclosed", "unknown", ""]:
                scores["budget"] = 10
        
        # Authority Score (30 points)
        if lead.authority_level:
            auth = lead.authority_level.lower()
            if "decision" in auth or "maker" in auth or "ceo" in auth or "owner" in auth:
                scores["authority"] = 30
            elif "influencer" in auth or "manager" in auth:
                scores["authority"] = 20
            elif "user" in auth or "end" in auth:
                scores["authority"] = 10
            elif "gatekeeper" in auth:
                scores["authority"] = 5
            else:
                scores["authority"] = 15
        
        # Need Score (25 points)
        need_score = 0
        if lead.interest_product and lead.interest_product.strip():
            need_score += 15
        if lead.notes and len(lead.notes) > 50:  # Detailed notes indicate clear need
            need_score += 10
        scores["need"] = min(need_score, 25)
        
        # Timeline Score (20 points)
        if lead.timeline:
            timeline = lead.timeline.lower()
            if any(x in timeline for x in ["immediate", "urgent", "asap", "now", "30 days"]):
                scores["timeline"] = 20
            elif any(x in timeline for x in ["60", "90", "quarter", "3 month"]):
                scores["timeline"] = 15
            elif any(x in timeline for x in ["6 month", "half year"]):
                scores["timeline"] = 10
            elif any(x in timeline for x in ["year", "12 month", "next year"]):
                scores["timeline"] = 5
            else:
                scores["timeline"] = 8
        
        total_score = sum(scores.values())
        
        # Determine qualification status
        if total_score >= QualificationService.QUALIFIED_THRESHOLD:
            status = "qualified"
        elif total_score >= QualificationService.PARTIALLY_QUALIFIED_THRESHOLD:
            status = "partially_qualified"
        else:
            status = "unqualified"
        
        return {
            "total_score": total_score,
            "max_score": 100,
            "percentage": total_score,
            "breakdown": scores,
            "status": status,
            "qualified": total_score >= QualificationService.QUALIFIED_THRESHOLD,
            "criteria_met": sum(1 for s in scores.values() if s > 0),
            "criteria_total": 4
        }
    
    @staticmethod
    def qualify_lead(
        lead_id: int,
        company_id: int,
        db: Session,
        user_id: Optional[int] = None
    ) -> Dict:
        """
        Qualify a lead and update its status
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            user_id: User performing qualification
            
        Returns:
            Qualification result
        """
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            return {"success": False, "error": "Lead not found"}
        
        # Calculate BANT score
        bant_result = QualificationService.calculate_bant_score(lead)
        
        # Update lead status based on qualification
        old_status = lead.status
        if bant_result["qualified"]:
            lead.status = "qualified"
        elif bant_result["status"] == "partially_qualified":
            lead.status = "contacted"  # Keep in pipeline
        
        # Log activity
        activity = Activity(
            company_id=company_id,
            lead_id=lead_id,
            activity_type="qualification",
            title=f"Lead Qualified: Score {bant_result['total_score']}/100",
            description=f"BANT Score: Budget={bant_result['breakdown']['budget']}, Authority={bant_result['breakdown']['authority']}, Need={bant_result['breakdown']['need']}, Timeline={bant_result['breakdown']['timeline']}. Status: {bant_result['status']}",
            outcome="positive" if bant_result["qualified"] else "neutral",
            user_id=user_id or lead.assigned_to,
            activity_date=datetime.utcnow()
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "lead_id": lead_id,
            "bant_score": bant_result,
            "old_status": old_status,
            "new_status": lead.status,
            "qualified_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_qualification_checklist(lead: Lead) -> Dict:
        """
        Get qualification checklist for a lead
        
        Args:
            lead: Lead object
            
        Returns:
            Checklist with completion status
        """
        checklist = {
            "budget": {
                "label": "Budget Range",
                "completed": bool(lead.budget_range and lead.budget_range.lower() not in ["not disclosed", "unknown", ""]),
                "value": lead.budget_range,
                "required": True
            },
            "authority": {
                "label": "Authority Level",
                "completed": bool(lead.authority_level),
                "value": lead.authority_level,
                "required": True
            },
            "need": {
                "label": "Need/Interest Product",
                "completed": bool(lead.interest_product and lead.interest_product.strip()),
                "value": lead.interest_product,
                "required": True
            },
            "timeline": {
                "label": "Timeline",
                "completed": bool(lead.timeline),
                "value": lead.timeline,
                "required": True
            },
            "contact_info": {
                "label": "Contact Information",
                "completed": bool(lead.email or lead.phone),
                "value": f"Email: {lead.email}, Phone: {lead.phone}",
                "required": True
            },
            "company": {
                "label": "Company Name",
                "completed": bool(lead.company_name),
                "value": lead.company_name,
                "required": False
            }
        }
        
        completed_count = sum(1 for item in checklist.values() if item["completed"])
        required_count = sum(1 for item in checklist.values() if item["required"])
        required_completed = sum(1 for item in checklist.values() if item["required"] and item["completed"])
        
        return {
            "checklist": checklist,
            "total_items": len(checklist),
            "completed_items": completed_count,
            "required_items": required_count,
            "required_completed": required_completed,
            "completion_percentage": round((completed_count / len(checklist)) * 100, 2),
            "ready_for_qualification": required_completed >= 3  # At least 3 of 5 required
        }
    
    @staticmethod
    def get_qualification_analytics(company_id: int, db: Session) -> Dict:
        """
        Get qualification analytics for a company
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Qualification analytics
        """
        # Total leads
        total_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id
        ).scalar() or 0
        
        # Qualified leads
        qualified_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.status == "qualified"
        ).scalar() or 0
        
        # Leads by status
        status_counts = {}
        for status in ["new", "contacted", "qualified", "converted", "disqualified"]:
            count = db.query(func.count(Lead.id)).filter(
                Lead.company_id == company_id,
                Lead.status == status
            ).scalar() or 0
            status_counts[status] = count
        
        # Leads with BANT data
        with_budget = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.budget_range.isnot(None),
            Lead.budget_range != ""
        ).scalar() or 0
        
        with_authority = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.authority_level.isnot(None)
        ).scalar() or 0
        
        with_timeline = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.timeline.isnot(None),
            Lead.timeline != ""
        ).scalar() or 0
        
        return {
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "qualification_rate": round((qualified_leads / total_leads * 100), 2) if total_leads > 0 else 0,
            "by_status": status_counts,
            "bant_completion": {
                "with_budget": with_budget,
                "with_authority": with_authority,
                "with_timeline": with_timeline,
                "budget_rate": round((with_budget / total_leads * 100), 2) if total_leads > 0 else 0,
                "authority_rate": round((with_authority / total_leads * 100), 2) if total_leads > 0 else 0,
                "timeline_rate": round((with_timeline / total_leads * 100), 2) if total_leads > 0 else 0
            }
        }
    
    @staticmethod
    def batch_qualify_leads(
        company_id: int,
        db: Session,
        lead_ids: Optional[List[int]] = None
    ) -> Dict:
        """
        Batch qualify multiple leads
        
        Args:
            company_id: Company ID
            db: Database session
            lead_ids: Optional list of lead IDs
            
        Returns:
            Batch qualification results
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
            "qualified": 0,
            "partially_qualified": 0,
            "unqualified": 0,
            "details": []
        }
        
        for lead in leads:
            bant_result = QualificationService.calculate_bant_score(lead)
            
            if bant_result["qualified"]:
                results["qualified"] += 1
                lead.status = "qualified"
            elif bant_result["status"] == "partially_qualified":
                results["partially_qualified"] += 1
            else:
                results["unqualified"] += 1
            
            results["details"].append({
                "lead_id": lead.id,
                "lead_name": lead.lead_name,
                "score": bant_result["total_score"],
                "status": bant_result["status"]
            })
        
        db.commit()
        
        return results
