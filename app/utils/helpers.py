"""
Helper Functions
"""

from datetime import datetime
from typing import Any, Optional
from math import ceil


def success_response(data: Any, message: str = "Success") -> dict:
    """
    Create success response
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Success response dictionary
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def error_response(error: str, details: Optional[dict] = None) -> dict:
    """
    Create error response
    
    Args:
        error: Error message
        details: Additional error details
        
    Returns:
        Error response dictionary
    """
    response = {
        "success": False,
        "error": error,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        response["details"] = details
    
    return response


def paginate(query, page: int = 1, per_page: int = 10):
    """
    Paginate database query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (starts from 1)
        per_page: Items per page
        
    Returns:
        Tuple of (items, pagination_meta)
    """
    # Ensure valid values
    page = max(1, page)
    per_page = min(max(1, per_page), 100)  # Max 100 items per page
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    pages = ceil(total / per_page) if total > 0 else 1
    offset = (page - 1) * per_page
    
    # Get items
    items = query.offset(offset).limit(per_page).all()
    
    # Pagination metadata
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages
    }
    
    return items, pagination


def generate_customer_code(company_id: int, customer_id: int) -> str:
    """
    Generate customer code
    
    Args:
        company_id: Company ID
        customer_id: Customer ID
        
    Returns:
        Customer code string
    """
    return f"CUST-{company_id:04d}-{customer_id:06d}"

