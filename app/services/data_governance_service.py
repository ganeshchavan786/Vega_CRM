"""
Data Governance Service
Manages data governance policies, compliance, and enforcement
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, Dict, List
from app.models.lead import Lead
from app.models.customer import Customer


class DataGovernanceService:
    """Service for data governance and compliance"""
    
    # Default governance policies
    DEFAULT_POLICIES = {
        "lead_required_fields": ["email", "lead_name"],
        "customer_required_fields": ["name", "email"],
        "contact_required_fields": ["name", "email"],
        "deal_required_fields": ["deal_name", "deal_value"],
        "max_lead_age_days": 180,
        "require_source_attribution": True,
        "require_consent_for_marketing": True,
        "data_retention_days": 365 * 3,  # 3 years
        "allow_duplicate_emails": False,
        "allow_duplicate_phones": False
    }
    
    @staticmethod
    def get_governance_policies(company_id: int, db: Session) -> Dict:
        """
        Get governance policies for a company
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Dictionary with governance policies
        """
        # In production, this would load from database
        # For now, return default policies
        return {
            "company_id": company_id,
            "policies": DataGovernanceService.DEFAULT_POLICIES,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def validate_against_policies(
        entity_type: str,
        data: Dict,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Validate data against governance policies
        
        Args:
            entity_type: Type of entity (lead, customer, contact, deal)
            data: Data to validate
            company_id: Company ID
            db: Database session
            
        Returns:
            Validation results
        """
        policies = DataGovernanceService.DEFAULT_POLICIES
        violations = []
        warnings = []
        
        # Get required fields for entity type
        required_fields_key = f"{entity_type}_required_fields"
        required_fields = policies.get(required_fields_key, [])
        
        # Check required fields
        for field in required_fields:
            if not data.get(field) or (isinstance(data.get(field), str) and not data.get(field).strip()):
                violations.append({
                    "field": field,
                    "rule": "required_field",
                    "message": f"Required field '{field}' is missing or empty"
                })
        
        # Check source attribution
        if entity_type == "lead" and policies.get("require_source_attribution"):
            if not data.get("source"):
                warnings.append({
                    "field": "source",
                    "rule": "source_attribution",
                    "message": "Source attribution is recommended but missing"
                })
        
        # Check consent for marketing
        if policies.get("require_consent_for_marketing"):
            if data.get("email") and not data.get("marketing_consent"):
                warnings.append({
                    "field": "marketing_consent",
                    "rule": "consent_required",
                    "message": "Marketing consent not provided for email contact"
                })
        
        # Check duplicate policy
        if entity_type == "lead":
            if not policies.get("allow_duplicate_emails") and data.get("email"):
                existing = db.query(Lead).filter(
                    Lead.company_id == company_id,
                    Lead.email == data.get("email")
                ).first()
                if existing:
                    violations.append({
                        "field": "email",
                        "rule": "no_duplicates",
                        "message": f"Duplicate email found (Lead ID: {existing.id})"
                    })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "entity_type": entity_type,
            "policies_applied": list(policies.keys())
        }
    
    @staticmethod
    def get_compliance_report(company_id: int, db: Session) -> Dict:
        """
        Get compliance report for a company
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Compliance report
        """
        policies = DataGovernanceService.DEFAULT_POLICIES
        
        # Check lead compliance
        total_leads = db.query(func.count(Lead.id)).filter(Lead.company_id == company_id).scalar() or 0
        
        leads_with_email = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.email.isnot(None),
            Lead.email != ""
        ).scalar() or 0
        
        leads_with_source = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.source.isnot(None),
            Lead.source != ""
        ).scalar() or 0
        
        # Check customer compliance
        total_customers = db.query(func.count(Customer.id)).filter(Customer.company_id == company_id).scalar() or 0
        
        customers_with_email = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.email.isnot(None),
            Customer.email != ""
        ).scalar() or 0
        
        # Calculate compliance scores
        lead_compliance = 0
        if total_leads > 0:
            email_compliance = (leads_with_email / total_leads) * 100
            source_compliance = (leads_with_source / total_leads) * 100 if policies.get("require_source_attribution") else 100
            lead_compliance = (email_compliance + source_compliance) / 2
        
        customer_compliance = 0
        if total_customers > 0:
            customer_compliance = (customers_with_email / total_customers) * 100
        
        overall_compliance = (lead_compliance + customer_compliance) / 2 if (total_leads + total_customers) > 0 else 100
        
        return {
            "company_id": company_id,
            "generated_at": datetime.utcnow().isoformat(),
            "overall_compliance": round(overall_compliance, 2),
            "compliance_grade": "A" if overall_compliance >= 90 else "B" if overall_compliance >= 75 else "C" if overall_compliance >= 60 else "D",
            "leads": {
                "total": total_leads,
                "with_required_email": leads_with_email,
                "with_source": leads_with_source,
                "compliance_score": round(lead_compliance, 2)
            },
            "customers": {
                "total": total_customers,
                "with_required_email": customers_with_email,
                "compliance_score": round(customer_compliance, 2)
            },
            "policies_checked": [
                "required_fields",
                "source_attribution",
                "duplicate_prevention"
            ]
        }
    
    @staticmethod
    def get_data_retention_report(company_id: int, db: Session) -> Dict:
        """
        Get data retention report
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Data retention report
        """
        from datetime import timedelta
        
        policies = DataGovernanceService.DEFAULT_POLICIES
        retention_days = policies.get("data_retention_days", 365 * 3)
        max_lead_age = policies.get("max_lead_age_days", 180)
        
        retention_cutoff = datetime.utcnow() - timedelta(days=retention_days)
        stale_cutoff = datetime.utcnow() - timedelta(days=max_lead_age)
        
        # Find records exceeding retention
        old_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.created_at < retention_cutoff
        ).scalar() or 0
        
        # Find stale leads (not converted, old)
        stale_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.status.notin_(["converted", "disqualified"]),
            Lead.updated_at < stale_cutoff
        ).scalar() or 0
        
        return {
            "company_id": company_id,
            "retention_policy_days": retention_days,
            "max_lead_age_days": max_lead_age,
            "records_exceeding_retention": {
                "leads": old_leads
            },
            "stale_records": {
                "leads": stale_leads
            },
            "recommendations": [
                f"Review {stale_leads} stale leads for conversion or disqualification" if stale_leads > 0 else None,
                f"Consider archiving {old_leads} old lead records" if old_leads > 0 else None
            ]
        }
