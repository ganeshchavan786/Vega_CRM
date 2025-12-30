"""
Data Quality Service
Monitors and reports on data quality across the CRM
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.contact import Contact
from app.models.deal import Deal


class DataQualityService:
    """Service for data quality monitoring and reporting"""
    
    @staticmethod
    def get_data_quality_metrics(company_id: int, db: Session) -> Dict:
        """
        Get comprehensive data quality metrics for a company
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            "leads": DataQualityService._get_lead_quality_metrics(company_id, db),
            "customers": DataQualityService._get_customer_quality_metrics(company_id, db),
            "contacts": DataQualityService._get_contact_quality_metrics(company_id, db),
            "deals": DataQualityService._get_deal_quality_metrics(company_id, db),
            "overall_score": 0,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Calculate overall score
        scores = [
            metrics["leads"]["quality_score"],
            metrics["customers"]["quality_score"],
            metrics["contacts"]["quality_score"],
            metrics["deals"]["quality_score"]
        ]
        metrics["overall_score"] = round(sum(scores) / len(scores), 2)
        
        return metrics
    
    @staticmethod
    def _get_lead_quality_metrics(company_id: int, db: Session) -> Dict:
        """Get lead data quality metrics"""
        total = db.query(func.count(Lead.id)).filter(Lead.company_id == company_id).scalar() or 0
        
        if total == 0:
            return {"total": 0, "quality_score": 100, "issues": []}
        
        # Check completeness
        with_email = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.email.isnot(None),
            Lead.email != ""
        ).scalar() or 0
        
        with_phone = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.phone.isnot(None),
            Lead.phone != ""
        ).scalar() or 0
        
        with_name = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            or_(
                and_(Lead.first_name.isnot(None), Lead.first_name != ""),
                and_(Lead.lead_name.isnot(None), Lead.lead_name != "")
            )
        ).scalar() or 0
        
        with_source = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.source.isnot(None),
            Lead.source != ""
        ).scalar() or 0
        
        # Calculate quality score
        email_pct = (with_email / total) * 100
        phone_pct = (with_phone / total) * 100
        name_pct = (with_name / total) * 100
        source_pct = (with_source / total) * 100
        
        quality_score = (email_pct * 0.3 + phone_pct * 0.25 + name_pct * 0.25 + source_pct * 0.2)
        
        issues = []
        if email_pct < 80:
            issues.append(f"{total - with_email} leads missing email")
        if phone_pct < 80:
            issues.append(f"{total - with_phone} leads missing phone")
        if name_pct < 90:
            issues.append(f"{total - with_name} leads missing name")
        if source_pct < 70:
            issues.append(f"{total - with_source} leads missing source")
        
        return {
            "total": total,
            "with_email": with_email,
            "with_phone": with_phone,
            "with_name": with_name,
            "with_source": with_source,
            "email_completeness": round(email_pct, 2),
            "phone_completeness": round(phone_pct, 2),
            "name_completeness": round(name_pct, 2),
            "source_completeness": round(source_pct, 2),
            "quality_score": round(quality_score, 2),
            "issues": issues
        }
    
    @staticmethod
    def _get_customer_quality_metrics(company_id: int, db: Session) -> Dict:
        """Get customer/account data quality metrics"""
        total = db.query(func.count(Customer.id)).filter(Customer.company_id == company_id).scalar() or 0
        
        if total == 0:
            return {"total": 0, "quality_score": 100, "issues": []}
        
        with_email = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.email.isnot(None),
            Customer.email != ""
        ).scalar() or 0
        
        with_phone = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.phone.isnot(None),
            Customer.phone != ""
        ).scalar() or 0
        
        with_industry = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.industry.isnot(None),
            Customer.industry != ""
        ).scalar() or 0
        
        with_address = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.address.isnot(None),
            Customer.address != ""
        ).scalar() or 0
        
        email_pct = (with_email / total) * 100
        phone_pct = (with_phone / total) * 100
        industry_pct = (with_industry / total) * 100
        address_pct = (with_address / total) * 100
        
        quality_score = (email_pct * 0.3 + phone_pct * 0.3 + industry_pct * 0.2 + address_pct * 0.2)
        
        issues = []
        if email_pct < 80:
            issues.append(f"{total - with_email} accounts missing email")
        if phone_pct < 80:
            issues.append(f"{total - with_phone} accounts missing phone")
        
        return {
            "total": total,
            "with_email": with_email,
            "with_phone": with_phone,
            "with_industry": with_industry,
            "with_address": with_address,
            "quality_score": round(quality_score, 2),
            "issues": issues
        }
    
    @staticmethod
    def _get_contact_quality_metrics(company_id: int, db: Session) -> Dict:
        """Get contact data quality metrics"""
        total = db.query(func.count(Contact.id)).filter(Contact.company_id == company_id).scalar() or 0
        
        if total == 0:
            return {"total": 0, "quality_score": 100, "issues": []}
        
        with_email = db.query(func.count(Contact.id)).filter(
            Contact.company_id == company_id,
            Contact.email.isnot(None),
            Contact.email != ""
        ).scalar() or 0
        
        with_phone = db.query(func.count(Contact.id)).filter(
            Contact.company_id == company_id,
            Contact.phone.isnot(None),
            Contact.phone != ""
        ).scalar() or 0
        
        with_account = db.query(func.count(Contact.id)).filter(
            Contact.company_id == company_id,
            Contact.account_id.isnot(None)
        ).scalar() or 0
        
        email_pct = (with_email / total) * 100
        phone_pct = (with_phone / total) * 100
        account_pct = (with_account / total) * 100
        
        quality_score = (email_pct * 0.4 + phone_pct * 0.3 + account_pct * 0.3)
        
        issues = []
        if email_pct < 90:
            issues.append(f"{total - with_email} contacts missing email")
        if account_pct < 80:
            issues.append(f"{total - with_account} contacts not linked to account")
        
        return {
            "total": total,
            "with_email": with_email,
            "with_phone": with_phone,
            "with_account": with_account,
            "quality_score": round(quality_score, 2),
            "issues": issues
        }
    
    @staticmethod
    def _get_deal_quality_metrics(company_id: int, db: Session) -> Dict:
        """Get deal/opportunity data quality metrics"""
        total = db.query(func.count(Deal.id)).filter(Deal.company_id == company_id).scalar() or 0
        
        if total == 0:
            return {"total": 0, "quality_score": 100, "issues": []}
        
        with_value = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.deal_value.isnot(None),
            Deal.deal_value > 0
        ).scalar() or 0
        
        with_close_date = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.expected_close_date.isnot(None)
        ).scalar() or 0
        
        with_account = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            or_(Deal.customer_id.isnot(None), Deal.account_id.isnot(None))
        ).scalar() or 0
        
        value_pct = (with_value / total) * 100
        date_pct = (with_close_date / total) * 100
        account_pct = (with_account / total) * 100
        
        quality_score = (value_pct * 0.4 + date_pct * 0.3 + account_pct * 0.3)
        
        issues = []
        if value_pct < 90:
            issues.append(f"{total - with_value} deals missing value")
        if date_pct < 80:
            issues.append(f"{total - with_close_date} deals missing close date")
        
        return {
            "total": total,
            "with_value": with_value,
            "with_close_date": with_close_date,
            "with_account": with_account,
            "quality_score": round(quality_score, 2),
            "issues": issues
        }
    
    @staticmethod
    def get_data_freshness_metrics(company_id: int, db: Session, days: int = 30) -> Dict:
        """
        Get data freshness metrics
        
        Args:
            company_id: Company ID
            db: Database session
            days: Number of days to consider as "fresh"
            
        Returns:
            Freshness metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Leads freshness
        total_leads = db.query(func.count(Lead.id)).filter(Lead.company_id == company_id).scalar() or 0
        fresh_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.updated_at >= cutoff_date
        ).scalar() or 0
        
        # Customers freshness
        total_customers = db.query(func.count(Customer.id)).filter(Customer.company_id == company_id).scalar() or 0
        fresh_customers = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.updated_at >= cutoff_date
        ).scalar() or 0
        
        # Deals freshness
        total_deals = db.query(func.count(Deal.id)).filter(Deal.company_id == company_id).scalar() or 0
        fresh_deals = db.query(func.count(Deal.id)).filter(
            Deal.company_id == company_id,
            Deal.updated_at >= cutoff_date
        ).scalar() or 0
        
        return {
            "period_days": days,
            "leads": {
                "total": total_leads,
                "fresh": fresh_leads,
                "stale": total_leads - fresh_leads,
                "freshness_pct": round((fresh_leads / total_leads * 100), 2) if total_leads > 0 else 100
            },
            "customers": {
                "total": total_customers,
                "fresh": fresh_customers,
                "stale": total_customers - fresh_customers,
                "freshness_pct": round((fresh_customers / total_customers * 100), 2) if total_customers > 0 else 100
            },
            "deals": {
                "total": total_deals,
                "fresh": fresh_deals,
                "stale": total_deals - fresh_deals,
                "freshness_pct": round((fresh_deals / total_deals * 100), 2) if total_deals > 0 else 100
            }
        }
    
    @staticmethod
    def get_duplicate_report(company_id: int, db: Session) -> Dict:
        """
        Get duplicate data report
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Duplicate report
        """
        # Find duplicate emails in leads
        lead_email_duplicates = db.query(
            Lead.email,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.company_id == company_id,
            Lead.email.isnot(None),
            Lead.email != ""
        ).group_by(Lead.email).having(func.count(Lead.id) > 1).all()
        
        # Find duplicate phones in leads
        lead_phone_duplicates = db.query(
            Lead.phone,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.company_id == company_id,
            Lead.phone.isnot(None),
            Lead.phone != ""
        ).group_by(Lead.phone).having(func.count(Lead.id) > 1).all()
        
        return {
            "leads": {
                "duplicate_emails": len(lead_email_duplicates),
                "duplicate_phones": len(lead_phone_duplicates),
                "email_duplicates": [{"email": e[0], "count": e[1]} for e in lead_email_duplicates[:10]],
                "phone_duplicates": [{"phone": p[0], "count": p[1]} for p in lead_phone_duplicates[:10]]
            }
        }
