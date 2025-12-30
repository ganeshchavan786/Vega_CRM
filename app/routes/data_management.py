"""
Data Management Routes
Handles data ingestion, quality, validation, and governance endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.models.user import User

router = APIRouter()


# Data Quality Endpoints

@router.get("/{company_id}/data-quality/metrics")
async def get_data_quality_metrics(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive data quality metrics
    
    Returns:
    - Quality scores for leads, customers, contacts, deals
    - Completeness metrics
    - Data issues
    """
    from app.services.data_quality_service import DataQualityService
    from app.models.user_company import UserCompany
    
    # Check access
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id
    ).first()
    
    if not user_company and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        metrics = DataQualityService.get_data_quality_metrics(company_id, db)
        return success_response(
            data=metrics,
            message="Data quality metrics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data quality metrics: {str(e)}"
        )


@router.get("/{company_id}/data-quality/freshness")
async def get_data_freshness(
    company_id: int = Path(..., description="Company ID"),
    days: int = Query(30, ge=1, le=365, description="Days to consider as fresh"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get data freshness metrics
    
    Returns:
    - Fresh vs stale records count
    - Freshness percentage by entity type
    """
    from app.services.data_quality_service import DataQualityService
    
    try:
        metrics = DataQualityService.get_data_freshness_metrics(company_id, db, days)
        return success_response(
            data=metrics,
            message="Data freshness metrics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data freshness: {str(e)}"
        )


@router.get("/{company_id}/data-quality/duplicates")
async def get_duplicate_report(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get duplicate data report
    
    Returns:
    - Duplicate emails and phones
    - Count of duplicates
    """
    from app.services.data_quality_service import DataQualityService
    
    try:
        report = DataQualityService.get_duplicate_report(company_id, db)
        return success_response(
            data=report,
            message="Duplicate report fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching duplicate report: {str(e)}"
        )


# Data Governance Endpoints

@router.get("/{company_id}/data-governance/policies")
async def get_governance_policies(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get data governance policies for company
    """
    from app.services.data_governance_service import DataGovernanceService
    
    try:
        policies = DataGovernanceService.get_governance_policies(company_id, db)
        return success_response(
            data=policies,
            message="Governance policies fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching governance policies: {str(e)}"
        )


@router.get("/{company_id}/data-governance/compliance")
async def get_compliance_report(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get compliance report
    
    Returns:
    - Overall compliance score
    - Compliance by entity type
    - Policies checked
    """
    from app.services.data_governance_service import DataGovernanceService
    
    try:
        report = DataGovernanceService.get_compliance_report(company_id, db)
        return success_response(
            data=report,
            message="Compliance report fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching compliance report: {str(e)}"
        )


@router.get("/{company_id}/data-governance/retention")
async def get_retention_report(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get data retention report
    
    Returns:
    - Records exceeding retention policy
    - Stale records
    - Recommendations
    """
    from app.services.data_governance_service import DataGovernanceService
    
    try:
        report = DataGovernanceService.get_data_retention_report(company_id, db)
        return success_response(
            data=report,
            message="Retention report fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching retention report: {str(e)}"
        )


@router.post("/{company_id}/data-governance/validate")
async def validate_data(
    company_id: int = Path(..., description="Company ID"),
    entity_type: str = Query(..., description="Entity type: lead, customer, contact, deal"),
    data: dict = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate data against governance policies
    
    Returns:
    - Validation result
    - Violations and warnings
    """
    from app.services.data_governance_service import DataGovernanceService
    
    valid_types = ["lead", "customer", "contact", "deal"]
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type. Must be one of: {', '.join(valid_types)}"
        )
    
    try:
        result = DataGovernanceService.validate_against_policies(
            entity_type=entity_type,
            data=data or {},
            company_id=company_id,
            db=db
        )
        return success_response(
            data=result,
            message="Validation complete"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating data: {str(e)}"
        )


# Data Ingestion Endpoints

@router.post("/{company_id}/data-ingestion/validate-utm")
async def validate_utm_parameters(
    company_id: int = Path(..., description="Company ID"),
    source: Optional[str] = Query(None),
    campaign: Optional[str] = Query(None),
    medium: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    content: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate UTM parameters for source attribution
    """
    from app.services.data_ingestion_service import DataIngestionService
    
    try:
        result = DataIngestionService.validate_utm_parameters({
            "source": source,
            "campaign": campaign,
            "medium": medium,
            "term": term,
            "content": content
        })
        return success_response(
            data=result,
            message="UTM validation complete"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating UTM: {str(e)}"
        )


@router.post("/{company_id}/data-ingestion/validate-consent")
async def validate_gdpr_consent(
    company_id: int = Path(..., description="Company ID"),
    email: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    email_consent: bool = Query(False),
    phone_consent: bool = Query(False),
    marketing_consent: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate GDPR consent fields
    """
    from app.services.data_ingestion_service import DataIngestionService
    
    try:
        result = DataIngestionService.validate_gdpr_consent({
            "email": email,
            "phone": phone,
            "email_consent": email_consent,
            "phone_consent": phone_consent,
            "marketing_consent": marketing_consent
        })
        return success_response(
            data=result,
            message="Consent validation complete"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating consent: {str(e)}"
        )


@router.post("/{company_id}/data-ingestion/check-dnd")
async def check_dnd_compliance(
    company_id: int = Path(..., description="Company ID"),
    phone: str = Query(..., description="Phone number to check"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check DND (Do Not Disturb) compliance for phone number
    """
    from app.services.data_ingestion_service import DataIngestionService
    
    try:
        result = DataIngestionService.check_dnd_compliance(phone, db)
        return success_response(
            data=result,
            message="DND check complete"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking DND: {str(e)}"
        )


@router.post("/{company_id}/data-ingestion/enrich")
async def enrich_lead_data(
    company_id: int = Path(..., description="Company ID"),
    data: dict = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Enrich lead data with additional information
    """
    from app.services.data_ingestion_service import DataIngestionService
    
    try:
        enriched = DataIngestionService.enrich_lead_data(data or {}, db)
        return success_response(
            data=enriched,
            message="Data enrichment complete"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enriching data: {str(e)}"
        )


@router.post("/{company_id}/data-ingestion/quality-score")
async def calculate_quality_score(
    company_id: int = Path(..., description="Company ID"),
    data: dict = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Calculate data quality score for a record
    """
    from app.services.data_ingestion_service import DataIngestionService
    
    try:
        score = DataIngestionService.calculate_data_quality_score(data or {})
        return success_response(
            data=score,
            message="Quality score calculated"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating quality score: {str(e)}"
        )


# Real-time Validation Endpoints

@router.post("/{company_id}/validation/check-duplicate")
async def check_duplicate(
    company_id: int = Path(..., description="Company ID"),
    email: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    company_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Real-time duplicate check
    """
    from app.utils.duplicate_detection import DuplicateDetection
    
    try:
        result = DuplicateDetection.find_duplicates(
            email=email,
            phone=phone,
            company_name=company_name,
            company_id=company_id,
            db=db
        )
        return success_response(
            data=result,
            message="Duplicate check complete"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking duplicates: {str(e)}"
        )


@router.post("/{company_id}/validation/validate-email")
async def validate_email(
    company_id: int = Path(..., description="Company ID"),
    email: str = Query(..., description="Email to validate"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate email format
    """
    import re
    
    result = {
        "email": email,
        "valid": False,
        "errors": [],
        "warnings": []
    }
    
    # Basic format check
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        result["errors"].append("Invalid email format")
    else:
        result["valid"] = True
        
        # Check for common typos
        domain = email.split("@")[1].lower()
        typo_domains = {
            "gmial.com": "gmail.com",
            "gmal.com": "gmail.com",
            "gamil.com": "gmail.com",
            "yaho.com": "yahoo.com",
            "hotmal.com": "hotmail.com"
        }
        if domain in typo_domains:
            result["warnings"].append(f"Possible typo: did you mean {typo_domains[domain]}?")
    
    return success_response(
        data=result,
        message="Email validation complete"
    )


@router.post("/{company_id}/validation/validate-phone")
async def validate_phone(
    company_id: int = Path(..., description="Company ID"),
    phone: str = Query(..., description="Phone to validate"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate phone number format
    """
    result = {
        "phone": phone,
        "valid": False,
        "formatted": None,
        "country": None,
        "errors": []
    }
    
    # Remove non-digits
    digits = "".join(filter(str.isdigit, phone))
    
    if len(digits) < 10:
        result["errors"].append("Phone number too short (minimum 10 digits)")
    elif len(digits) > 15:
        result["errors"].append("Phone number too long (maximum 15 digits)")
    else:
        result["valid"] = True
        
        # Detect country
        if phone.startswith("+91") or (len(digits) == 10 and digits[0] in "6789"):
            result["country"] = "India"
            result["formatted"] = f"+91 {digits[-10:-5]} {digits[-5:]}"
        elif phone.startswith("+1"):
            result["country"] = "USA/Canada"
            result["formatted"] = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
        else:
            result["formatted"] = digits
    
    return success_response(
        data=result,
        message="Phone validation complete"
    )
