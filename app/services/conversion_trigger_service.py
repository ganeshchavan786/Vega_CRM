"""
Conversion Trigger Service
Handles automatic conversion triggers, validation, and conversion automation
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.activity import Activity


class ConversionTriggerService:
    """Service for automatic lead conversion triggers"""
    
    # Conversion Criteria
    MIN_SCORE_FOR_CONVERSION = 70
    REQUIRED_STATUS = "contacted"
    
    @staticmethod
    def check_conversion_eligibility(lead: Lead, db: Session) -> Dict:
        """
        Check if a lead is eligible for conversion
        
        Conversion Rules:
        1. Lead Score >= 70
        2. Lead Status = "contacted" or "qualified"
        3. Has email or phone
        4. BANT criteria met (at least 3/4)
        
        Args:
            lead: Lead object
            db: Database session
            
        Returns:
            Eligibility result
        """
        criteria = {
            "score_threshold": {
                "met": False,
                "required": ConversionTriggerService.MIN_SCORE_FOR_CONVERSION,
                "actual": lead.lead_score or 0,
                "message": ""
            },
            "status_requirement": {
                "met": False,
                "required": ["contacted", "qualified"],
                "actual": lead.status,
                "message": ""
            },
            "contact_info": {
                "met": False,
                "required": "email or phone",
                "actual": f"Email: {lead.email}, Phone: {lead.phone}",
                "message": ""
            },
            "bant_criteria": {
                "met": False,
                "required": "3/4 BANT criteria",
                "actual": 0,
                "message": ""
            }
        }
        
        # Check score threshold
        if (lead.lead_score or 0) >= ConversionTriggerService.MIN_SCORE_FOR_CONVERSION:
            criteria["score_threshold"]["met"] = True
            criteria["score_threshold"]["message"] = "Score threshold met"
        else:
            criteria["score_threshold"]["message"] = f"Score {lead.lead_score or 0} is below {ConversionTriggerService.MIN_SCORE_FOR_CONVERSION}"
        
        # Check status
        if lead.status in ["contacted", "qualified"]:
            criteria["status_requirement"]["met"] = True
            criteria["status_requirement"]["message"] = "Status is valid for conversion"
        else:
            criteria["status_requirement"]["message"] = f"Status '{lead.status}' is not eligible for conversion"
        
        # Check contact info
        if lead.email or lead.phone:
            criteria["contact_info"]["met"] = True
            criteria["contact_info"]["message"] = "Contact information available"
        else:
            criteria["contact_info"]["message"] = "No email or phone available"
        
        # Check BANT criteria
        bant_count = 0
        if lead.budget_range and lead.budget_range.lower() not in ["not disclosed", "unknown", ""]:
            bant_count += 1
        if lead.authority_level:
            bant_count += 1
        if lead.interest_product and lead.interest_product.strip():
            bant_count += 1
        if lead.timeline:
            bant_count += 1
        
        criteria["bant_criteria"]["actual"] = f"{bant_count}/4"
        if bant_count >= 3:
            criteria["bant_criteria"]["met"] = True
            criteria["bant_criteria"]["message"] = f"BANT criteria met ({bant_count}/4)"
        else:
            criteria["bant_criteria"]["message"] = f"Only {bant_count}/4 BANT criteria met"
        
        # Calculate overall eligibility
        met_count = sum(1 for c in criteria.values() if c["met"])
        eligible = met_count >= 3  # At least 3 of 4 criteria must be met
        
        return {
            "eligible": eligible,
            "criteria": criteria,
            "criteria_met": met_count,
            "criteria_total": 4,
            "can_convert": eligible,
            "blocking_issues": [c["message"] for c in criteria.values() if not c["met"]]
        }
    
    @staticmethod
    def get_conversion_ready_leads(company_id: int, db: Session) -> List[Dict]:
        """
        Get all leads ready for conversion
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            List of conversion-ready leads
        """
        leads = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status.in_(["contacted", "qualified"]),
            Lead.lead_score >= ConversionTriggerService.MIN_SCORE_FOR_CONVERSION
        ).all()
        
        ready_leads = []
        for lead in leads:
            eligibility = ConversionTriggerService.check_conversion_eligibility(lead, db)
            if eligibility["eligible"]:
                ready_leads.append({
                    "lead_id": lead.id,
                    "lead_name": lead.lead_name,
                    "email": lead.email,
                    "phone": lead.phone,
                    "company_name": lead.company_name,
                    "lead_score": lead.lead_score,
                    "status": lead.status,
                    "criteria_met": eligibility["criteria_met"],
                    "created_at": lead.created_at.isoformat() if lead.created_at else None
                })
        
        return ready_leads
    
    @staticmethod
    def auto_trigger_conversion(
        lead_id: int,
        company_id: int,
        user_id: int,
        db: Session
    ) -> Dict:
        """
        Automatically trigger conversion for an eligible lead
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            user_id: User ID performing conversion
            db: Database session
            
        Returns:
            Conversion result
        """
        from app.utils.lead_conversion import LeadConversionService
        
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            return {"success": False, "error": "Lead not found"}
        
        # Check eligibility
        eligibility = ConversionTriggerService.check_conversion_eligibility(lead, db)
        if not eligibility["eligible"]:
            return {
                "success": False,
                "error": "Lead not eligible for conversion",
                "blocking_issues": eligibility["blocking_issues"]
            }
        
        # Perform conversion
        try:
            result = LeadConversionService.convert_lead_to_account(
                lead_id=lead_id,
                company_id=company_id,
                user_id=user_id,
                db=db
            )
            
            # Log auto-conversion activity
            activity = Activity(
                company_id=company_id,
                lead_id=lead_id,
                activity_type="conversion",
                title="Auto-Conversion Triggered",
                description=f"Lead automatically converted. Score: {lead.lead_score}, Criteria met: {eligibility['criteria_met']}/4",
                outcome="positive",
                user_id=user_id,
                activity_date=datetime.utcnow()
            )
            db.add(activity)
            db.commit()
            
            return {
                "success": True,
                "lead_id": lead_id,
                "conversion_result": result,
                "triggered_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def batch_check_conversion_triggers(company_id: int, db: Session) -> Dict:
        """
        Batch check conversion triggers for all eligible leads
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Batch check results
        """
        leads = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status.notin_(["converted", "disqualified"])
        ).all()
        
        results = {
            "total_checked": len(leads),
            "eligible_for_conversion": 0,
            "not_eligible": 0,
            "eligible_leads": [],
            "common_blocking_issues": {}
        }
        
        for lead in leads:
            eligibility = ConversionTriggerService.check_conversion_eligibility(lead, db)
            
            if eligibility["eligible"]:
                results["eligible_for_conversion"] += 1
                results["eligible_leads"].append({
                    "lead_id": lead.id,
                    "lead_name": lead.lead_name,
                    "score": lead.lead_score
                })
            else:
                results["not_eligible"] += 1
                for issue in eligibility["blocking_issues"]:
                    results["common_blocking_issues"][issue] = results["common_blocking_issues"].get(issue, 0) + 1
        
        return results
    
    @staticmethod
    def get_conversion_analytics(company_id: int, db: Session, days: int = 30) -> Dict:
        """
        Get conversion analytics
        
        Args:
            company_id: Company ID
            db: Database session
            days: Number of days to analyze
            
        Returns:
            Conversion analytics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Total leads
        total_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id
        ).scalar() or 0
        
        # Converted leads
        converted_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.status == "converted"
        ).scalar() or 0
        
        # Converted in period
        converted_in_period = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.status == "converted",
            Lead.updated_at >= cutoff
        ).scalar() or 0
        
        # Leads created in period
        created_in_period = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.created_at >= cutoff
        ).scalar() or 0
        
        # Average score of converted leads
        avg_converted_score = db.query(func.avg(Lead.lead_score)).filter(
            Lead.company_id == company_id,
            Lead.status == "converted"
        ).scalar() or 0
        
        # Conversion-ready leads
        ready_leads = ConversionTriggerService.get_conversion_ready_leads(company_id, db)
        
        return {
            "period_days": days,
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "conversion_rate": round((converted_leads / total_leads * 100), 2) if total_leads > 0 else 0,
            "converted_in_period": converted_in_period,
            "created_in_period": created_in_period,
            "period_conversion_rate": round((converted_in_period / created_in_period * 100), 2) if created_in_period > 0 else 0,
            "avg_converted_score": round(float(avg_converted_score), 2),
            "conversion_ready_count": len(ready_leads),
            "conversion_ready_leads": ready_leads[:10]  # Top 10
        }
    
    @staticmethod
    def set_conversion_reminder(
        lead_id: int,
        company_id: int,
        user_id: int,
        db: Session,
        days_delay: int = 3
    ) -> Dict:
        """
        Set a reminder for lead conversion
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            user_id: User ID
            db: Database session
            days_delay: Days until reminder
            
        Returns:
            Reminder result
        """
        from app.models.task import Task
        
        lead = db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.company_id == company_id
        ).first()
        
        if not lead:
            return {"success": False, "error": "Lead not found"}
        
        # Create reminder task
        task = Task(
            company_id=company_id,
            title=f"Convert Lead: {lead.lead_name}",
            description=f"Lead is ready for conversion. Score: {lead.lead_score}. Review and convert to account.",
            task_type="follow_up",
            priority="high",
            status="pending",
            due_date=datetime.utcnow() + timedelta(days=days_delay),
            assigned_to=user_id,
            lead_id=lead_id,
            created_by=user_id
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return {
            "success": True,
            "task_id": task.id,
            "lead_id": lead_id,
            "reminder_date": task.due_date.isoformat()
        }
