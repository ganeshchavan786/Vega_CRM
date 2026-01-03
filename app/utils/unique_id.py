"""
Unique ID Generator Utility
Generates unique IDs in format: PREFIX-C{company_id}-{DD-MM-YYYY}-{sequence}
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from typing import Dict, Optional


# Module prefixes configuration
MODULE_PREFIXES = {
    'customer': 'ACC',      # Accounts
    'contact': 'CON',       # Contacts
    'lead': 'LEAD',         # Leads
    'deal': 'OPP',          # Opportunities (Deals)
    'task': 'TASK',         # Tasks
    'activity': 'ACT',      # Activities
    'report': 'RPT',        # Reports
}


def get_next_sequence(db: Session, prefix: str, company_id: int, date_str: str) -> int:
    """
    Get next sequence number for a module, company, and date
    Sequence is continuous (no daily reset)
    """
    # Query to get the highest sequence for this module and company
    query = f"""
        SELECT MAX(CAST(SUBSTR(unique_id, -5) AS INTEGER)) as max_seq
        FROM (
            SELECT unique_id 
            FROM customers WHERE unique_id LIKE '{prefix}-C{company_id}-%'
            UNION ALL
            SELECT unique_id 
            FROM contacts WHERE unique_id LIKE '{prefix}-C{company_id}-%'
            UNION ALL
            SELECT unique_id 
            FROM leads WHERE unique_id LIKE '{prefix}-C{company_id}-%'
            UNION ALL
            SELECT unique_id 
            FROM deals WHERE unique_id LIKE '{prefix}-C{company_id}-%'
            UNION ALL
            SELECT unique_id 
            FROM tasks WHERE unique_id LIKE '{prefix}-C{company_id}-%'
            UNION ALL
            SELECT unique_id 
            FROM activities WHERE unique_id LIKE '{prefix}-C{company_id}-%'
            UNION ALL
            SELECT unique_id 
            FROM reports WHERE unique_id LIKE '{prefix}-C{company_id}-%'
        )
    """
    
    try:
        result = db.execute(query).fetchone()
        max_seq = result[0] if result and result[0] else 0
        return max_seq + 1
    except Exception:
        # If tables don't exist yet or no records, start from 1
        return 1


def generate_unique_id(
    module: str, 
    company_id: int, 
    created_date: Optional[datetime] = None,
    db: Optional[Session] = None
) -> str:
    """
    Generate unique ID for a record
    
    Args:
        module: Module name ('customer', 'contact', 'lead', etc.)
        company_id: Company ID
        created_date: Creation date (defaults to current date)
        db: Database session (required for sequence tracking)
    
    Returns:
        Unique ID string in format: PREFIX-C{company_id}-{DD-MM-YYYY}-{sequence}
    
    Example:
        generate_unique_id('lead', 1) -> "LEAD-C1-03-01-2026-00001"
    """
    
    # Validate module
    if module not in MODULE_PREFIXES:
        raise ValueError(f"Unknown module: {module}. Available modules: {list(MODULE_PREFIXES.keys())}")
    
    # Get prefix
    prefix = MODULE_PREFIXES[module]
    
    # Use current date if not provided
    if created_date is None:
        created_date = datetime.now()
    
    # Format date as DD-MM-YYYY
    date_str = created_date.strftime("%d-%m-%Y")
    
    # Get database session if not provided
    if db is None:
        db = next(get_db())
    
    # Get next sequence number
    sequence = get_next_sequence(db, prefix, company_id, date_str)
    
    # Format sequence with leading zeros (5 digits)
    sequence_str = f"{sequence:05d}"
    
    # Generate unique ID
    unique_id = f"{prefix}-C{company_id}-{date_str}-{sequence_str}"
    
    return unique_id


def parse_unique_id(unique_id: str) -> Dict[str, str]:
    """
    Parse unique ID to extract components
    
    Args:
        unique_id: Unique ID string (e.g., "LEAD-C1-03-01-2026-00001")
    
    Returns:
        Dictionary with parsed components
    """
    try:
        parts = unique_id.split('-')
        if len(parts) != 4:
            raise ValueError("Invalid unique ID format")
        
        prefix = parts[0]
        company_part = parts[1]
        date_part = parts[2]
        sequence_part = parts[3]
        
        # Extract company ID from "C1" format
        if not company_part.startswith('C'):
            raise ValueError("Invalid company format")
        company_id = company_part[1:]
        
        # Validate date format
        datetime.strptime(date_part, "%d-%m-%Y")
        
        return {
            'prefix': prefix,
            'company_id': company_id,
            'date': date_part,
            'sequence': sequence_part,
            'module': get_module_from_prefix(prefix)
        }
    except Exception as e:
        raise ValueError(f"Failed to parse unique ID '{unique_id}': {str(e)}")


def get_module_from_prefix(prefix: str) -> str:
    """
    Get module name from prefix
    
    Args:
        prefix: Module prefix (e.g., 'LEAD')
    
    Returns:
        Module name (e.g., 'lead')
    """
    for module, module_prefix in MODULE_PREFIXES.items():
        if module_prefix == prefix:
            return module
    raise ValueError(f"Unknown prefix: {prefix}")


def validate_unique_id(unique_id: str) -> bool:
    """
    Validate unique ID format
    
    Args:
        unique_id: Unique ID string to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        parse_unique_id(unique_id)
        return True
    except ValueError:
        return False


# Convenience functions for each module
def generate_account_id(company_id: int, created_date: Optional[datetime] = None, db: Optional[Session] = None) -> str:
    """Generate Account ID: ACC-C1-03-01-2026-00001"""
    return generate_unique_id('customer', company_id, created_date, db)


def generate_contact_id(company_id: int, created_date: Optional[datetime] = None, db: Optional[Session] = None) -> str:
    """Generate Contact ID: CON-C1-03-01-2026-00001"""
    return generate_unique_id('contact', company_id, created_date, db)


def generate_lead_id(company_id: int, created_date: Optional[datetime] = None, db: Optional[Session] = None) -> str:
    """Generate Lead ID: LEAD-C1-03-01-2026-00001"""
    return generate_unique_id('lead', company_id, created_date, db)


def generate_opportunity_id(company_id: int, created_date: Optional[datetime] = None, db: Optional[Session] = None) -> str:
    """Generate Opportunity ID: OPP-C1-03-01-2026-00001"""
    return generate_unique_id('deal', company_id, created_date, db)


def generate_task_id(company_id: int, created_date: Optional[datetime] = None, db: Optional[Session] = None) -> str:
    """Generate Task ID: TASK-C1-03-01-2026-00001"""
    return generate_unique_id('task', company_id, created_date, db)


def generate_activity_id(company_id: int, created_date: Optional[datetime] = None, db: Optional[Session] = None) -> str:
    """Generate Activity ID: ACT-C1-03-01-2026-00001"""
    return generate_unique_id('activity', company_id, created_date, db)


def generate_report_id(company_id: int, created_date: Optional[datetime] = None, db: Optional[Session] = None) -> str:
    """Generate Report ID: RPT-C1-03-01-2026-00001"""
    return generate_unique_id('report', company_id, created_date, db)
