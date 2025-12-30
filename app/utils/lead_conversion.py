"""
Lead Conversion Workflow
One-click conversion: Lead → Account → Contact → Opportunity
Follows Account-First Model
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.activity import Activity
from app.models.user import User
from app.utils.nurturing_automation import NurturingAutomation


class LeadConversionService:
    """Lead conversion workflow service"""
    
    @staticmethod
    def convert_lead_to_account(
        lead_id: int,
        company_id: int,
        current_user: User,
        db: Session,
        skip_eligibility_check: bool = False
    ) -> Dict:
        """
        Convert lead to account following Account-First Model
        
        Process:
        1. Check conversion eligibility
        2. Create Account (Customer) from Lead
        3. Create Contact from Lead
        4. Link Contact to Account
        5. Create Opportunity (Deal) from Lead
        6. Log Initial Activity
        7. Update Lead status to "Converted"
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            current_user: Current user performing conversion
            db: Database session
            skip_eligibility_check: Skip eligibility check (admin only)
            
        Returns:
            Dictionary with conversion results
        """
        # Get lead
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            raise ValueError("Lead not found")
        
        # Check if already converted
        if lead.status == "converted":
            raise ValueError("Lead already converted")
        
        # Check eligibility (unless skipped)
        if not skip_eligibility_check:
            eligibility = NurturingAutomation.check_conversion_eligibility(
                lead_id, company_id, db
            )
            
            if not eligibility["eligible"]:
                raise ValueError(f"Lead not eligible for conversion: {eligibility['reason']}")
        
        conversion_results = {
            "account": None,
            "contact": None,
            "deal": None,
            "activity": None,
            "lead_updated": False
        }
        
        try:
            # Step 1: Create Account (Customer) from Lead
            account_name = lead.company_name or f"{lead.first_name} {lead.last_name}".strip() or "Unknown Company"
            
            # Check if account already exists (by name)
            existing_account = db.query(Customer).filter(
                and_(
                    Customer.company_id == company_id,
                    Customer.name == account_name
                )
            ).first()
            
            if existing_account:
                # Use existing account
                account = existing_account
                conversion_results["account"] = {
                    "id": account.id,
                    "name": account.name,
                    "created": False,
                    "message": "Used existing account"
                }
            else:
                # Create new account
                account = Customer(
                    company_id=company_id,
                    name=account_name,
                    email=lead.email if lead.email else None,
                    phone=lead.phone if lead.phone else None,
                    country=lead.country if lead.country else None,
                    account_type="customer",  # Converted lead becomes customer
                    status="active",
                    industry=lead.industry if hasattr(lead, 'industry') and lead.industry else None,
                    company_size=lead.company_size if hasattr(lead, 'company_size') and lead.company_size else None,
                    assigned_to=lead.assigned_to,
                    created_by=current_user.id
                )
                
                db.add(account)
                db.flush()  # Get account ID
                
                conversion_results["account"] = {
                    "id": account.id,
                    "name": account.name,
                    "created": True
                }
            
            # Step 2: Create Contact from Lead
            contact_name = f"{lead.first_name} {lead.last_name}".strip() if (lead.first_name or lead.last_name) else lead.lead_name or "Unknown Contact"
            
            contact = Contact(
                company_id=company_id,
                account_id=account.id,
                name=contact_name,
                email=lead.email if lead.email else None,
                phone=lead.phone if lead.phone else None,
                job_title=lead.job_title if hasattr(lead, 'job_title') and lead.job_title else None,
                role=lead.authority_level if hasattr(lead, 'authority_level') and lead.authority_level else "user",
                is_primary_contact=True,  # First contact is primary
                created_by=current_user.id
            )
            
            db.add(contact)
            db.flush()  # Get contact ID
            
            conversion_results["contact"] = {
                "id": contact.id,
                "name": contact.name,
                "account_id": account.id
            }
            
            # Step 3: Create Opportunity (Deal) from Lead
            # Parse budget range to get deal value (if available)
            deal_value = 0
            if hasattr(lead, 'budget_range') and lead.budget_range:
                # Try to extract numeric value from budget range
                # Example: "₹5-7 Lakh" -> 600000 (average)
                import re
                numbers = re.findall(r'\d+', lead.budget_range)
                if numbers:
                    # Take average if range, or single value
                    if len(numbers) >= 2:
                        deal_value = (int(numbers[0]) + int(numbers[1])) / 2 * 100000  # Assume lakhs
                    else:
                        deal_value = int(numbers[0]) * 100000  # Assume lakhs
            
            # Default deal value if not parsed
            if deal_value == 0:
                deal_value = 50000  # Default
            
            # Parse timeline to get close date
            close_date = None
            if hasattr(lead, 'timeline') and lead.timeline:
                # Try to extract days/months from timeline
                # Example: "3-6 Months" -> 4.5 months from now
                import re
                numbers = re.findall(r'\d+', lead.timeline)
                if numbers:
                    if len(numbers) >= 2:
                        months = (int(numbers[0]) + int(numbers[1])) / 2
                    else:
                        months = int(numbers[0])
                    close_date = datetime.utcnow() + timedelta(days=int(months * 30))
            
            # Default close date if not parsed (30 days from now)
            if not close_date:
                close_date = datetime.utcnow() + timedelta(days=30)
            
            deal = Deal(
                company_id=company_id,
                customer_id=account.id,
                account_id=account.id,
                primary_contact_id=contact.id,
                lead_id=lead.id,
                deal_name=f"{account_name} - {lead.interest_product or 'Opportunity'}" if hasattr(lead, 'interest_product') and lead.interest_product else f"{account_name} - Opportunity",
                deal_value=deal_value,
                currency="INR",  # Default, can be configured
                stage="prospect",  # Start at prospect stage
                probability=25,  # Default probability
                expected_close_date=close_date.date() if isinstance(close_date, datetime) else close_date,
                status="open",
                assigned_to=lead.assigned_to,
                created_by=current_user.id,
                notes=f"Converted from Lead #{lead.id}: {lead.notes or 'No notes'}" if hasattr(lead, 'notes') and lead.notes else f"Converted from Lead #{lead.id}"
            )
            
            db.add(deal)
            db.flush()  # Get deal ID
            
            conversion_results["deal"] = {
                "id": deal.id,
                "name": deal.deal_name,
                "value": float(deal.deal_value),
                "account_id": account.id,
                "contact_id": contact.id
            }
            
            # Step 4: Log Initial Activity
            activity = Activity(
                company_id=company_id,
                customer_id=account.id,
                lead_id=lead.id,
                deal_id=deal.id,
                activity_type="note",
                title="Lead Converted to Account",
                description=f"Lead '{lead.full_name}' converted to Account '{account.name}'. Created Contact '{contact.name}' and Opportunity '{deal.deal_name}'.",
                user_id=current_user.id
            )
            
            db.add(activity)
            db.flush()
            
            conversion_results["activity"] = {
                "id": activity.id,
                "title": activity.title
            }
            
            # Step 5: Update Lead status to "Converted"
            lead.status = "converted"
            lead.stage = "converted"
            lead.converted_to_account_id = account.id
            lead.converted_at = datetime.utcnow()
            
            conversion_results["lead_updated"] = True
            
            # Commit all changes
            db.commit()
            
            return {
                "success": True,
                "message": "Lead converted successfully",
                "conversion_results": conversion_results
            }
            
        except Exception as e:
            db.rollback()
            raise ValueError(f"Conversion failed: {str(e)}")
    
    @staticmethod
    def get_conversion_preview(
        lead_id: int,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Get preview of what will be created during conversion
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            
        Returns:
            Dictionary with conversion preview
        """
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            raise ValueError("Lead not found")
        
        account_name = lead.company_name or f"{lead.first_name} {lead.last_name}".strip() or "Unknown Company"
        contact_name = f"{lead.first_name} {lead.last_name}".strip() if (lead.first_name or lead.last_name) else lead.lead_name or "Unknown Contact"
        
        # Parse budget for deal value
        deal_value = 0
        if hasattr(lead, 'budget_range') and lead.budget_range:
            import re
            numbers = re.findall(r'\d+', lead.budget_range)
            if numbers:
                if len(numbers) >= 2:
                    deal_value = (int(numbers[0]) + int(numbers[1])) / 2 * 100000
                else:
                    deal_value = int(numbers[0]) * 100000
        
        if deal_value == 0:
            deal_value = 50000
        
        # Parse timeline for close date
        close_date = None
        if hasattr(lead, 'timeline') and lead.timeline:
            import re
            numbers = re.findall(r'\d+', lead.timeline)
            if numbers:
                if len(numbers) >= 2:
                    months = (int(numbers[0]) + int(numbers[1])) / 2
                else:
                    months = int(numbers[0])
                close_date = datetime.utcnow() + timedelta(days=int(months * 30))
        
        if not close_date:
            close_date = datetime.utcnow() + timedelta(days=30)
        
        deal_name = f"{account_name} - {lead.interest_product or 'Opportunity'}" if hasattr(lead, 'interest_product') and lead.interest_product else f"{account_name} - Opportunity"
        
        return {
            "account": {
                "name": account_name,
                "email": lead.email,
                "phone": lead.phone,
                "country": lead.country,
                "account_type": "customer"
            },
            "contact": {
                "name": contact_name,
                "email": lead.email,
                "phone": lead.phone,
                "job_title": lead.job_title if hasattr(lead, 'job_title') and lead.job_title else None,
                "role": lead.authority_level if hasattr(lead, 'authority_level') and lead.authority_level else "user",
                "is_primary": True
            },
            "deal": {
                "name": deal_name,
                "value": deal_value,
                "currency": "INR",
                "stage": "prospect",
                "probability": 25,
                "expected_close_date": close_date.date().isoformat() if isinstance(close_date, datetime) else close_date.isoformat() if hasattr(close_date, 'isoformat') else str(close_date)
            }
        }
    
    @staticmethod
    def batch_convert_leads(
        lead_ids: list,
        company_id: int,
        current_user: User,
        db: Session,
        skip_eligibility_check: bool = False
    ) -> Dict:
        """
        Batch convert multiple leads to accounts
        
        Args:
            lead_ids: List of Lead IDs to convert
            company_id: Company ID
            current_user: Current user performing conversion
            db: Database session
            skip_eligibility_check: Skip eligibility check
            
        Returns:
            Dictionary with batch conversion results
        """
        results = {
            "total": len(lead_ids),
            "successful": 0,
            "failed": 0,
            "conversions": [],
            "errors": []
        }
        
        for lead_id in lead_ids:
            try:
                conversion = LeadConversionService.convert_lead_to_account(
                    lead_id=lead_id,
                    company_id=company_id,
                    current_user=current_user,
                    db=db,
                    skip_eligibility_check=skip_eligibility_check
                )
                results["successful"] += 1
                results["conversions"].append({
                    "lead_id": lead_id,
                    "success": True,
                    "result": conversion
                })
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "lead_id": lead_id,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    @staticmethod
    def get_conversion_analytics(
        company_id: int,
        db: Session,
        days: int = 30
    ) -> Dict:
        """
        Get lead conversion analytics
        
        Args:
            company_id: Company ID
            db: Database session
            days: Number of days to analyze
            
        Returns:
            Dictionary with conversion analytics
        """
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total leads in period
        total_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.created_at >= start_date
        ).scalar() or 0
        
        # Converted leads in period
        converted_leads = db.query(func.count(Lead.id)).filter(
            Lead.company_id == company_id,
            Lead.status == "converted",
            Lead.converted_at >= start_date
        ).scalar() or 0
        
        # Conversion rate
        conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Average time to convert (in days)
        converted_with_time = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status == "converted",
            Lead.converted_at.isnot(None),
            Lead.created_at.isnot(None)
        ).all()
        
        avg_conversion_time = 0
        if converted_with_time:
            total_days = sum(
                (lead.converted_at - lead.created_at).days 
                for lead in converted_with_time 
                if lead.converted_at and lead.created_at
            )
            avg_conversion_time = total_days / len(converted_with_time) if converted_with_time else 0
        
        # Leads by status
        leads_by_status = {}
        statuses = ["new", "contacted", "qualified", "proposal", "negotiation", "converted", "lost"]
        for status in statuses:
            count = db.query(func.count(Lead.id)).filter(
                Lead.company_id == company_id,
                Lead.status == status
            ).scalar() or 0
            leads_by_status[status] = count
        
        # Conversion by source
        conversion_by_source = db.query(
            Lead.source,
            func.count(Lead.id).label('total'),
            func.sum(func.cast(Lead.status == "converted", db.bind.dialect.name == 'sqlite' and 'INTEGER' or 'INT')).label('converted')
        ).filter(
            Lead.company_id == company_id
        ).group_by(Lead.source).all()
        
        source_analytics = []
        for row in conversion_by_source:
            source_analytics.append({
                "source": row[0] or "Unknown",
                "total": row[1],
                "converted": row[2] or 0,
                "rate": (row[2] / row[1] * 100) if row[1] > 0 and row[2] else 0
            })
        
        return {
            "period_days": days,
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "conversion_rate": round(conversion_rate, 2),
            "avg_conversion_time_days": round(avg_conversion_time, 1),
            "leads_by_status": leads_by_status,
            "conversion_by_source": source_analytics
        }
    
    @staticmethod
    def validate_conversion(
        lead_id: int,
        company_id: int,
        db: Session
    ) -> Dict:
        """
        Validate if lead can be converted
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            
        Returns:
            Dictionary with validation results
        """
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            return {
                "valid": False,
                "errors": ["Lead not found"],
                "warnings": []
            }
        
        errors = []
        warnings = []
        
        # Check if already converted
        if lead.status == "converted":
            errors.append("Lead is already converted")
        
        # Check required fields
        if not lead.email and not lead.phone:
            errors.append("Lead must have email or phone")
        
        if not lead.lead_name and not (lead.first_name or lead.last_name):
            errors.append("Lead must have a name")
        
        # Check eligibility
        eligibility = NurturingAutomation.check_conversion_eligibility(
            lead_id, company_id, db
        )
        
        if not eligibility["eligible"]:
            warnings.append(f"Lead may not be ready: {eligibility['reason']}")
        
        # Check for duplicate account
        account_name = lead.company_name or f"{lead.first_name} {lead.last_name}".strip()
        if account_name:
            existing = db.query(Customer).filter(
                Customer.company_id == company_id,
                Customer.name == account_name
            ).first()
            if existing:
                warnings.append(f"Account '{account_name}' already exists - will link to existing")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "lead_score": lead.lead_score if hasattr(lead, 'lead_score') else None,
            "lead_status": lead.status
        }
