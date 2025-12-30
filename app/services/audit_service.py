"""
Audit Trail Service
Handles all audit trail logging and retrieval
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from app.models.audit_trail import AuditTrail
import json


def serialize_value(value):
    """Convert non-JSON-serializable types to serializable ones"""
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, date):
        return value.isoformat()
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    elif hasattr(value, '__dict__'):
        return str(value)
    return value


def serialize_dict(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Recursively serialize dictionary values for JSON storage"""
    if data is None:
        return None
    
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = serialize_dict(value)
        elif isinstance(value, list):
            result[key] = [serialize_value(v) for v in value]
        else:
            result[key] = serialize_value(value)
    return result


def create_audit_trail(
    db: Session,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    action: str = "UNKNOWN",
    resource_type: str = "UNKNOWN",
    resource_id: Optional[int] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "SUCCESS",
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditTrail:
    """
    Create a new audit trail entry
    """
    # Serialize values to handle Decimal and other non-JSON types
    serialized_old = serialize_dict(old_values)
    serialized_new = serialize_dict(new_values)
    serialized_details = serialize_dict(details)
    
    audit_entry = AuditTrail(
        user_id=user_id,
        user_email=user_email,
        action=action.upper(),
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=serialized_old,
        new_values=serialized_new,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status.upper(),
        message=message,
        details=serialized_details,
        timestamp=datetime.utcnow()
    )
    
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    
    return audit_entry


def log_create(
    db: Session,
    user_id: Optional[int],
    user_email: Optional[str],
    resource_type: str,
    resource_id: int,
    new_values: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditTrail:
    """
    Log a CREATE action
    """
    if not message:
        message = f"{resource_type} #{resource_id} created"
    
    return create_audit_trail(
        db=db,
        user_id=user_id,
        user_email=user_email,
        action="CREATE",
        resource_type=resource_type,
        resource_id=resource_id,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        status="SUCCESS",
        message=message,
        details=details
    )


def log_update(
    db: Session,
    user_id: Optional[int],
    user_email: Optional[str],
    resource_type: str,
    resource_id: int,
    old_values: Dict[str, Any],
    new_values: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditTrail:
    """
    Log an UPDATE action
    """
    if not message:
        # Find what changed
        changed_fields = []
        for key, new_val in new_values.items():
            old_val = old_values.get(key)
            if old_val != new_val:
                changed_fields.append(key)
        
        if changed_fields:
            message = f"{resource_type} #{resource_id} updated: {', '.join(changed_fields)}"
        else:
            message = f"{resource_type} #{resource_id} updated"
    
    return create_audit_trail(
        db=db,
        user_id=user_id,
        user_email=user_email,
        action="UPDATE",
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        status="SUCCESS",
        message=message,
        details=details
    )


def log_delete(
    db: Session,
    user_id: Optional[int],
    user_email: Optional[str],
    resource_type: str,
    resource_id: int,
    old_values: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditTrail:
    """
    Log a DELETE action
    """
    if not message:
        message = f"{resource_type} #{resource_id} deleted"
    
    return create_audit_trail(
        db=db,
        user_id=user_id,
        user_email=user_email,
        action="DELETE",
        resource_type=resource_type,
        resource_id=resource_id,
        old_values=old_values,
        ip_address=ip_address,
        user_agent=user_agent,
        status="SUCCESS",
        message=message,
        details=details
    )


def log_custom_event(
    db: Session,
    user_id: Optional[int],
    user_email: Optional[str],
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "SUCCESS",
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditTrail:
    """
    Log a custom event (LOGIN, LOGOUT, IMPORT, EXPORT, etc.)
    """
    return create_audit_trail(
        db=db,
        user_id=user_id,
        user_email=user_email,
        action=action.upper(),
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status.upper(),
        message=message,
        details=details
    )


def get_audit_trails(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
) -> tuple[List[AuditTrail], int]:
    """
    Get audit trails with filtering and pagination
    Returns: (list of audit trails, total count)
    """
    query = db.query(AuditTrail)
    
    # Apply filters
    if start_date:
        query = query.filter(AuditTrail.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditTrail.timestamp <= end_date)
    
    if user_id:
        query = query.filter(AuditTrail.user_id == user_id)
    
    if user_email:
        query = query.filter(AuditTrail.user_email.ilike(f"%{user_email}%"))
    
    if action:
        query = query.filter(AuditTrail.action == action.upper())
    
    if resource_type:
        query = query.filter(AuditTrail.resource_type == resource_type)
    
    if resource_id:
        query = query.filter(AuditTrail.resource_id == resource_id)
    
    if status:
        query = query.filter(AuditTrail.status == status.upper())
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                AuditTrail.message.ilike(search_term),
                AuditTrail.user_email.ilike(search_term),
                AuditTrail.resource_type.ilike(search_term)
            )
        )
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination and ordering
    audit_trails = query.order_by(desc(AuditTrail.timestamp)).offset(skip).limit(limit).all()
    
    return audit_trails, total_count


def get_resource_history(
    db: Session,
    resource_type: str,
    resource_id: int,
    limit: int = 50
) -> List[AuditTrail]:
    """
    Get audit history for a specific resource
    """
    return db.query(AuditTrail).filter(
        AuditTrail.resource_type == resource_type,
        AuditTrail.resource_id == resource_id
    ).order_by(desc(AuditTrail.timestamp)).limit(limit).all()


def get_user_activity(
    db: Session,
    user_id: int,
    limit: int = 100
) -> List[AuditTrail]:
    """
    Get all activities for a specific user
    """
    return db.query(AuditTrail).filter(
        AuditTrail.user_id == user_id
    ).order_by(desc(AuditTrail.timestamp)).limit(limit).all()

