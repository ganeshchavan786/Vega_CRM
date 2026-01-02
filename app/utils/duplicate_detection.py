"""
Duplicate Detection Engine
Real-time duplicate detection for leads using Email + Phone + Company (fuzzy matching)
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict
from difflib import SequenceMatcher
from app.models.lead import Lead


class DuplicateDetectionEngine:
    """Detect duplicate leads using Email + Phone + Company combination"""
    
    # Similarity thresholds
    EMAIL_EXACT_MATCH = True  # Email must match exactly
    PHONE_SIMILARITY_THRESHOLD = 0.98  # Phone numbers must be 98% similar (almost exact match)
    COMPANY_SIMILARITY_THRESHOLD = 0.85  # Company names must be 85% similar (fuzzy matching)
    
    @staticmethod
    def normalize_string(text: Optional[str]) -> str:
        """
        Normalize string for comparison
        
        Args:
            text: String to normalize
            
        Returns:
            Normalized string (lowercase, stripped, spaces normalized)
        """
        if not text:
            return ""
        return " ".join(text.lower().strip().split())
    
    @staticmethod
    def normalize_phone(phone: Optional[str]) -> str:
        """
        Normalize phone number for comparison
        
        Args:
            phone: Phone number to normalize
            
        Returns:
            Normalized phone (digits only)
        """
        if not phone:
            return ""
        # Remove all non-digit characters
        return "".join(filter(str.isdigit, phone))
    
    @staticmethod
    def normalize_email(email: Optional[str]) -> str:
        """
        Normalize email for comparison
        
        Args:
            email: Email to normalize
            
        Returns:
            Normalized email (lowercase, stripped)
        """
        if not email:
            return ""
        return email.lower().strip()
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings using SequenceMatcher
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        if not str1 or not str2:
            return 0.0
        
        return SequenceMatcher(None, str1, str2).ratio()
    
    @staticmethod
    def check_duplicate(
        company_id: int,
        email: Optional[str],
        phone: Optional[str],
        company_name: Optional[str],
        db: Session,
        exclude_lead_id: Optional[int] = None
    ) -> Dict:
        """
        Check for duplicate leads based on Email + Phone + Company
        
        Matching rules:
        1. Email must match exactly (if both provided)
        2. Phone must be similar (90%+ similarity, if both provided)
        3. Company name must be similar (85%+ similarity, fuzzy matching, if both provided)
        
        Args:
            company_id: Company ID
            email: Lead email
            phone: Lead phone
            company_name: Lead company name
            db: Database session
            exclude_lead_id: Lead ID to exclude from check (for updates)
            
        Returns:
            Dictionary with duplicate information:
            {
                "is_duplicate": bool,
                "duplicate_leads": List[Lead],
                "match_reason": str,
                "confidence": str  # "high", "medium", "low"
            }
        """
        email_norm = DuplicateDetectionEngine.normalize_email(email)
        phone_norm = DuplicateDetectionEngine.normalize_phone(phone)
        company_norm = DuplicateDetectionEngine.normalize_string(company_name)
        
        # Build query
        query = db.query(Lead).filter(
            and_(
                Lead.company_id == company_id,
                Lead.is_duplicate == False  # Don't check already marked duplicates
            )
        )
        
        # Exclude current lead if updating
        if exclude_lead_id:
            query = query.filter(Lead.id != exclude_lead_id)
        
        all_leads = query.all()
        
        duplicate_leads = []
        match_reasons = []
        confidence_levels = []
        
        for existing_lead in all_leads:
            match_score = 0
            match_reason_parts = []
            confidence = "low"
            
            # Check email match (exact)
            if email_norm and existing_lead.email:
                existing_email_norm = DuplicateDetectionEngine.normalize_email(existing_lead.email)
                if email_norm == existing_email_norm:
                    match_score += 3
                    match_reason_parts.append("email")
                    confidence = "high"
            
            # Check phone match (similarity)
            if phone_norm and existing_lead.phone:
                existing_phone_norm = DuplicateDetectionEngine.normalize_phone(existing_lead.phone)
                if existing_phone_norm and len(existing_phone_norm) >= 10:  # Valid phone
                    phone_similarity = DuplicateDetectionEngine.calculate_similarity(
                        phone_norm, existing_phone_norm
                    )
                    if phone_similarity >= DuplicateDetectionEngine.PHONE_SIMILARITY_THRESHOLD:
                        match_score += 2
                        match_reason_parts.append("phone")
                        if confidence == "low":
                            confidence = "medium"
            
            # Check company name match (fuzzy)
            if company_norm and existing_lead.company_name:
                existing_company_norm = DuplicateDetectionEngine.normalize_string(existing_lead.company_name)
                if existing_company_norm:
                    company_similarity = DuplicateDetectionEngine.calculate_similarity(
                        company_norm, existing_company_norm
                    )
                    if company_similarity >= DuplicateDetectionEngine.COMPANY_SIMILARITY_THRESHOLD:
                        match_score += 2
                        match_reason_parts.append("company")
                        if confidence == "low":
                            confidence = "medium"
            
            # Check name match (first + last name)
            if email_norm or phone_norm:  # Only if we have email or phone
                existing_first = DuplicateDetectionEngine.normalize_string(existing_lead.first_name)
                existing_last = DuplicateDetectionEngine.normalize_string(existing_lead.last_name)
                # This is a bonus check, not primary
                if existing_first and existing_last:
                    # Could add name matching here if needed
                    pass
            
            # Determine if duplicate (need at least 2 matches or email + one other)
            is_match = False
            
            # High confidence: Email + Phone or Email + Company
            if email_norm and existing_lead.email:
                if (phone_norm and existing_lead.phone and 
                    DuplicateDetectionEngine.calculate_similarity(
                        phone_norm, 
                        DuplicateDetectionEngine.normalize_phone(existing_lead.phone)
                    ) >= DuplicateDetectionEngine.PHONE_SIMILARITY_THRESHOLD):
                    is_match = True
                elif (company_norm and existing_lead.company_name and
                      DuplicateDetectionEngine.calculate_similarity(
                          company_norm,
                          DuplicateDetectionEngine.normalize_string(existing_lead.company_name)
                      ) >= DuplicateDetectionEngine.COMPANY_SIMILARITY_THRESHOLD):
                    is_match = True
            
            # Medium confidence: Phone + Company (both similar)
            elif phone_norm and company_norm and existing_lead.phone and existing_lead.company_name:
                phone_sim = DuplicateDetectionEngine.calculate_similarity(
                    phone_norm,
                    DuplicateDetectionEngine.normalize_phone(existing_lead.phone)
                )
                company_sim = DuplicateDetectionEngine.calculate_similarity(
                    company_norm,
                    DuplicateDetectionEngine.normalize_string(existing_lead.company_name)
                )
                if (phone_sim >= DuplicateDetectionEngine.PHONE_SIMILARITY_THRESHOLD and
                    company_sim >= DuplicateDetectionEngine.COMPANY_SIMILARITY_THRESHOLD):
                    is_match = True
            
            if is_match:
                duplicate_leads.append(existing_lead)
                match_reasons.append(" + ".join(match_reason_parts) if match_reason_parts else "multiple fields")
                confidence_levels.append(confidence)
        
        # Determine overall confidence
        overall_confidence = "low"
        if confidence_levels:
            if "high" in confidence_levels:
                overall_confidence = "high"
            elif "medium" in confidence_levels:
                overall_confidence = "medium"
        
        return {
            "is_duplicate": len(duplicate_leads) > 0,
            "duplicate_leads": duplicate_leads,
            "match_reason": ", ".join(set(match_reasons)) if match_reasons else "No matches",
            "confidence": overall_confidence,
            "match_count": len(duplicate_leads)
        }
    
    @staticmethod
    def mark_as_duplicate(
        lead_id: int,
        company_id: int,
        db: Session,
        is_duplicate: bool = True
    ) -> bool:
        """
        Mark lead as duplicate or not
        
        Args:
            lead_id: Lead ID
            company_id: Company ID
            db: Database session
            is_duplicate: True to mark as duplicate, False to unmark
            
        Returns:
            True if updated, False if lead not found
        """
        lead = db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not lead:
            return False
        
        lead.is_duplicate = is_duplicate
        db.commit()
        
        return True
    
    @staticmethod
    def detect_and_mark_duplicates(
        company_id: int,
        db: Session,
        auto_mark: bool = False
    ) -> Dict:
        """
        Scan all leads and detect/mark duplicates
        
        Args:
            company_id: Company ID
            db: Database session
            auto_mark: If True, automatically mark duplicates
            
        Returns:
            Dictionary with detection results
        """
        leads = db.query(Lead).filter(
            and_(
                Lead.company_id == company_id,
                Lead.is_duplicate == False  # Only check non-duplicates
            )
        ).all()
        
        duplicates_found = 0
        duplicates_marked = 0
        duplicate_groups = []
        
        processed_lead_ids = set()
        
        for lead in leads:
            if lead.id in processed_lead_ids:
                continue
            
            # Check for duplicates
            result = DuplicateDetectionEngine.check_duplicate(
                company_id=company_id,
                email=lead.email,
                phone=lead.phone,
                company_name=lead.company_name,
                db=db,
                exclude_lead_id=lead.id
            )
            
            if result["is_duplicate"]:
                duplicates_found += 1
                duplicate_group = {
                    "primary_lead_id": lead.id,
                    "primary_lead_name": lead.full_name,
                    "duplicate_lead_ids": [d.id for d in result["duplicate_leads"]],
                    "duplicate_lead_names": [d.full_name for d in result["duplicate_leads"]],
                    "match_reason": result["match_reason"],
                    "confidence": result["confidence"]
                }
                duplicate_groups.append(duplicate_group)
                
                # Mark duplicates if auto_mark is True
                if auto_mark:
                    # Mark the duplicate leads (not the primary)
                    for dup_lead in result["duplicate_leads"]:
                        if not dup_lead.is_duplicate:
                            dup_lead.is_duplicate = True
                            duplicates_marked += 1
                            processed_lead_ids.add(dup_lead.id)
        
        if auto_mark:
            db.commit()
        
        return {
            "total_leads_checked": len(leads),
            "duplicate_groups_found": duplicates_found,
            "duplicates_marked": duplicates_marked,
            "duplicate_groups": duplicate_groups
        }
    
    @staticmethod
    def merge_duplicates(
        primary_lead_id: int,
        duplicate_lead_ids: List[int],
        company_id: int,
        db: Session
    ) -> bool:
        """
        Merge duplicate leads into primary lead
        
        Args:
            primary_lead_id: ID of lead to keep
            duplicate_lead_ids: List of duplicate lead IDs to merge
            company_id: Company ID
            db: Database session
            
        Returns:
            True if merged successfully
        """
        primary_lead = db.query(Lead).filter(
            and_(
                Lead.id == primary_lead_id,
                Lead.company_id == company_id
            )
        ).first()
        
        if not primary_lead:
            return False
        
        # Merge data from duplicates (take best values)
        for dup_id in duplicate_lead_ids:
            dup_lead = db.query(Lead).filter(
                and_(
                    Lead.id == dup_id,
                    Lead.company_id == company_id
                )
            ).first()
            
            if not dup_lead:
                continue
            
            # Merge fields (keep primary, fill missing from duplicate)
            if not primary_lead.email and dup_lead.email:
                primary_lead.email = dup_lead.email
            if not primary_lead.phone and dup_lead.phone:
                primary_lead.phone = dup_lead.phone
            if not primary_lead.company_name and dup_lead.company_name:
                primary_lead.company_name = dup_lead.company_name
            if not primary_lead.first_name and dup_lead.first_name:
                primary_lead.first_name = dup_lead.first_name
            if not primary_lead.last_name and dup_lead.last_name:
                primary_lead.last_name = dup_lead.last_name
            
            # Merge notes
            if dup_lead.notes:
                if primary_lead.notes:
                    primary_lead.notes += f"\n\n--- Merged from Lead #{dup_id} ---\n{dup_lead.notes}"
                else:
                    primary_lead.notes = f"--- Merged from Lead #{dup_id} ---\n{dup_lead.notes}"
            
            # Take higher score
            if dup_lead.lead_score and (not primary_lead.lead_score or dup_lead.lead_score > primary_lead.lead_score):
                primary_lead.lead_score = dup_lead.lead_score
            
            # Mark duplicate as merged and inactive
            dup_lead.is_duplicate = True
            dup_lead.status = "disqualified"
            # Could add a merged_into_lead_id field if needed
        
        db.commit()
        
        return True


