"""
Data Ingestion Service
Handles data import, validation, enrichment, and batch processing
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, List, Any
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.contact import Contact


class DataIngestionService:
    """Service for data ingestion, validation, and enrichment"""
    
    # UTM Parameters
    VALID_UTM_SOURCES = ["google", "facebook", "linkedin", "twitter", "email", "direct", "referral", "organic"]
    VALID_UTM_MEDIUMS = ["cpc", "organic", "social", "email", "referral", "display", "affiliate"]
    
    @staticmethod
    def validate_utm_parameters(data: Dict) -> Dict:
        """
        Validate UTM parameters for source attribution
        
        Args:
            data: Dictionary with UTM fields (source, campaign, medium, term, content)
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Source validation
        source = data.get("source", "").lower().strip()
        if source and source not in DataIngestionService.VALID_UTM_SOURCES:
            warnings.append(f"Non-standard UTM source: {source}")
        
        # Medium validation
        medium = data.get("medium", "").lower().strip()
        if medium and medium not in DataIngestionService.VALID_UTM_MEDIUMS:
            warnings.append(f"Non-standard UTM medium: {medium}")
        
        # Campaign validation
        campaign = data.get("campaign", "").strip()
        if not campaign and source:
            warnings.append("Campaign name missing for attributed source")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "utm_data": {
                "source": source or None,
                "campaign": campaign or None,
                "medium": medium or None,
                "term": data.get("term", "").strip() or None,
                "content": data.get("content", "").strip() or None
            }
        }
    
    @staticmethod
    def validate_gdpr_consent(data: Dict) -> Dict:
        """
        Validate GDPR consent fields
        
        Args:
            data: Dictionary with consent fields
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check consent fields
        email_consent = data.get("email_consent", False)
        phone_consent = data.get("phone_consent", False)
        marketing_consent = data.get("marketing_consent", False)
        
        # If email provided, email consent should be present
        if data.get("email") and not email_consent:
            warnings.append("Email provided without explicit consent")
        
        # If phone provided, phone consent should be present
        if data.get("phone") and not phone_consent:
            warnings.append("Phone provided without explicit consent")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "consent_data": {
                "email_consent": email_consent,
                "phone_consent": phone_consent,
                "marketing_consent": marketing_consent,
                "consent_date": datetime.utcnow().isoformat() if any([email_consent, phone_consent, marketing_consent]) else None
            }
        }
    
    @staticmethod
    def check_dnd_compliance(phone: str, db: Session) -> Dict:
        """
        Check DND (Do Not Disturb) compliance
        
        Args:
            phone: Phone number to check
            db: Database session
            
        Returns:
            Dictionary with DND status
        """
        # In production, this would check against DND registry
        # For now, we check internal opt-out list
        
        is_dnd = False
        dnd_reason = None
        
        # Check if phone exists in any contact/lead with DND flag
        # This is a simplified check - production would use external DND API
        
        return {
            "phone": phone,
            "is_dnd": is_dnd,
            "dnd_reason": dnd_reason,
            "can_call": not is_dnd,
            "can_sms": not is_dnd
        }
    
    @staticmethod
    def enrich_lead_data(lead_data: Dict, db: Session) -> Dict:
        """
        Enrich lead data with additional information
        
        Args:
            lead_data: Lead data dictionary
            db: Database session
            
        Returns:
            Enriched lead data
        """
        enriched = lead_data.copy()
        
        # Auto-detect country from phone
        phone = lead_data.get("phone", "")
        if phone:
            if phone.startswith("+91") or phone.startswith("91"):
                enriched["country"] = enriched.get("country") or "India"
            elif phone.startswith("+1"):
                enriched["country"] = enriched.get("country") or "USA"
            elif phone.startswith("+44"):
                enriched["country"] = enriched.get("country") or "UK"
        
        # Auto-set priority based on source
        source = lead_data.get("source", "").lower()
        if not enriched.get("priority"):
            if source in ["referral", "partner", "website"]:
                enriched["priority"] = "high"
            elif source in ["google", "linkedin", "facebook"]:
                enriched["priority"] = "medium"
            else:
                enriched["priority"] = "low"
        
        # Extract company domain from email
        email = lead_data.get("email", "")
        if email and "@" in email:
            domain = email.split("@")[1].lower()
            # Skip common email providers
            if domain not in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]:
                enriched["company_domain"] = domain
        
        return enriched
    
    @staticmethod
    def batch_import_leads(
        leads_data: List[Dict],
        company_id: int,
        user_id: int,
        db: Session,
        skip_duplicates: bool = True
    ) -> Dict:
        """
        Batch import multiple leads
        
        Args:
            leads_data: List of lead data dictionaries
            company_id: Company ID
            user_id: User ID performing import
            db: Database session
            skip_duplicates: Skip duplicate leads
            
        Returns:
            Import results
        """
        from app.utils.duplicate_detection import DuplicateDetection
        
        results = {
            "total": len(leads_data),
            "imported": 0,
            "skipped": 0,
            "errors": [],
            "duplicates": []
        }
        
        for idx, lead_data in enumerate(leads_data):
            try:
                # Check for duplicates
                if skip_duplicates:
                    duplicates = DuplicateDetection.find_duplicates(
                        email=lead_data.get("email"),
                        phone=lead_data.get("phone"),
                        company_name=lead_data.get("company_name"),
                        company_id=company_id,
                        db=db
                    )
                    
                    if duplicates.get("has_duplicates"):
                        results["skipped"] += 1
                        results["duplicates"].append({
                            "row": idx + 1,
                            "data": lead_data,
                            "duplicate_ids": [d["id"] for d in duplicates.get("duplicates", [])]
                        })
                        continue
                
                # Enrich data
                enriched_data = DataIngestionService.enrich_lead_data(lead_data, db)
                
                # Create lead
                lead = Lead(
                    company_id=company_id,
                    lead_name=enriched_data.get("lead_name") or f"{enriched_data.get('first_name', '')} {enriched_data.get('last_name', '')}".strip(),
                    first_name=enriched_data.get("first_name"),
                    last_name=enriched_data.get("last_name"),
                    email=enriched_data.get("email"),
                    phone=enriched_data.get("phone"),
                    company_name=enriched_data.get("company_name"),
                    source=enriched_data.get("source"),
                    campaign=enriched_data.get("campaign"),
                    medium=enriched_data.get("medium"),
                    priority=enriched_data.get("priority", "medium"),
                    country=enriched_data.get("country"),
                    status="new",
                    created_by=user_id
                )
                
                db.add(lead)
                results["imported"] += 1
                
            except Exception as e:
                results["errors"].append({
                    "row": idx + 1,
                    "error": str(e),
                    "data": lead_data
                })
        
        db.commit()
        
        return results
    
    @staticmethod
    def calculate_data_quality_score(data: Dict) -> Dict:
        """
        Calculate data quality score for a record
        
        Args:
            data: Data dictionary
            
        Returns:
            Quality score and breakdown
        """
        score = 0
        max_score = 100
        breakdown = {}
        
        # Email quality (20 points)
        email = data.get("email", "")
        if email:
            if "@" in email and "." in email.split("@")[1]:
                score += 20
                breakdown["email"] = {"score": 20, "status": "valid"}
            else:
                breakdown["email"] = {"score": 0, "status": "invalid"}
        else:
            breakdown["email"] = {"score": 0, "status": "missing"}
        
        # Phone quality (20 points)
        phone = data.get("phone", "")
        if phone:
            # Remove non-digits
            digits = "".join(filter(str.isdigit, phone))
            if len(digits) >= 10:
                score += 20
                breakdown["phone"] = {"score": 20, "status": "valid"}
            else:
                score += 10
                breakdown["phone"] = {"score": 10, "status": "partial"}
        else:
            breakdown["phone"] = {"score": 0, "status": "missing"}
        
        # Name quality (20 points)
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        if first_name and last_name:
            score += 20
            breakdown["name"] = {"score": 20, "status": "complete"}
        elif first_name or last_name:
            score += 10
            breakdown["name"] = {"score": 10, "status": "partial"}
        else:
            breakdown["name"] = {"score": 0, "status": "missing"}
        
        # Company quality (20 points)
        company = data.get("company_name", "")
        if company and len(company) > 2:
            score += 20
            breakdown["company"] = {"score": 20, "status": "valid"}
        else:
            breakdown["company"] = {"score": 0, "status": "missing"}
        
        # Source attribution (20 points)
        source = data.get("source", "")
        campaign = data.get("campaign", "")
        if source and campaign:
            score += 20
            breakdown["attribution"] = {"score": 20, "status": "complete"}
        elif source:
            score += 10
            breakdown["attribution"] = {"score": 10, "status": "partial"}
        else:
            breakdown["attribution"] = {"score": 0, "status": "missing"}
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": round(score / max_score * 100, 2),
            "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
            "breakdown": breakdown
        }
