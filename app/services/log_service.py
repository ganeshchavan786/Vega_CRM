"""
Logging Service
Handles all logging operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from app.models.log import Log


def create_log(
    db: Session,
    level: str,
    category: str,
    action: str,
    message: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict] = None,
    status: str = "Success"
) -> Log:
    """
    Create a new log entry
    """
    log = Log(
        level=level,
        category=category,
        action=action,
        message=message,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        details=details,
        status=status,
        timestamp=datetime.utcnow()
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    level: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
) -> List[Log]:
    """
    Get logs with filters
    """
    query = db.query(Log)
    
    # Apply filters
    if level:
        query = query.filter(Log.level == level)
    
    if category:
        query = query.filter(Log.category == category)
    
    if user_id:
        query = query.filter(Log.user_id == user_id)
    
    if start_date:
        query = query.filter(Log.timestamp >= start_date)
    
    if end_date:
        query = query.filter(Log.timestamp <= end_date)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Log.message.ilike(search_pattern),
                Log.action.ilike(search_pattern),
                Log.user_email.ilike(search_pattern),
                Log.ip_address.ilike(search_pattern)
            )
        )
    
    # Order by timestamp descending (newest first)
    query = query.order_by(desc(Log.timestamp))
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


def get_logs_count(
    db: Session,
    level: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
) -> int:
    """
    Get total count of logs matching filters
    """
    query = db.query(Log)
    
    # Apply same filters as get_logs
    if level:
        query = query.filter(Log.level == level)
    
    if category:
        query = query.filter(Log.category == category)
    
    if user_id:
        query = query.filter(Log.user_id == user_id)
    
    if start_date:
        query = query.filter(Log.timestamp >= start_date)
    
    if end_date:
        query = query.filter(Log.timestamp <= end_date)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Log.message.ilike(search_pattern),
                Log.action.ilike(search_pattern),
                Log.user_email.ilike(search_pattern),
                Log.ip_address.ilike(search_pattern)
            )
        )
    
    return query.count()


def get_log_statistics(db: Session, days: int = 7) -> Dict:
    """
    Get log statistics for dashboard
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total logs
    total_logs = db.query(Log).filter(Log.timestamp >= start_date).count()
    
    # Logs by level
    error_count = db.query(Log).filter(
        and_(Log.timestamp >= start_date, Log.level == "ERROR")
    ).count()
    
    warning_count = db.query(Log).filter(
        and_(Log.timestamp >= start_date, Log.level == "WARNING")
    ).count()
    
    info_count = db.query(Log).filter(
        and_(Log.timestamp >= start_date, Log.level == "INFO")
    ).count()
    
    # Logs by category
    auth_logs = db.query(Log).filter(
        and_(Log.timestamp >= start_date, Log.category == "Auth")
    ).count()
    
    email_logs = db.query(Log).filter(
        and_(Log.timestamp >= start_date, Log.category == "Email")
    ).count()
    
    failed_logins = db.query(Log).filter(
        and_(
            Log.timestamp >= start_date,
            Log.category == "Auth",
            Log.action == "Login Failed"
        )
    ).count()
    
    failed_emails = db.query(Log).filter(
        and_(
            Log.timestamp >= start_date,
            Log.category == "Email",
            Log.status == "Failed"
        )
    ).count()
    
    return {
        "total_logs": total_logs,
        "error_count": error_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "auth_logs": auth_logs,
        "email_logs": email_logs,
        "failed_logins": failed_logins,
        "failed_emails": failed_emails,
        "period_days": days
    }


def cleanup_old_logs(db: Session, days: int = 90) -> int:
    """
    Delete logs older than specified days
    Returns count of deleted logs
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    deleted_count = db.query(Log).filter(Log.timestamp < cutoff_date).delete()
    db.commit()
    
    return deleted_count


def get_recent_logs(db: Session, limit: int = 50) -> List[Log]:
    """
    Get most recent logs
    """
    return db.query(Log).order_by(desc(Log.timestamp)).limit(limit).all()


# Helper functions for easy logging
def log_info(
    db: Session,
    category: str,
    action: str,
    message: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict] = None
) -> Log:
    """Log INFO level message"""
    return create_log(
        db=db,
        level="INFO",
        category=category,
        action=action,
        message=message,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        details=details
    )


def log_warning(
    db: Session,
    category: str,
    action: str,
    message: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict] = None
) -> Log:
    """Log WARNING level message"""
    return create_log(
        db=db,
        level="WARNING",
        category=category,
        action=action,
        message=message,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        details=details
    )


def log_error(
    db: Session,
    category: str,
    action: str,
    message: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict] = None
) -> Log:
    """Log ERROR level message"""
    return create_log(
        db=db,
        level="ERROR",
        category=category,
        action=action,
        message=message,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        details=details
    )


def log_debug(
    db: Session,
    category: str,
    action: str,
    message: str,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict] = None
) -> Log:
    """Log DEBUG level message"""
    return create_log(
        db=db,
        level="DEBUG",
        category=category,
        action=action,
        message=message,
        user_id=user_id,
        user_email=user_email,
        ip_address=ip_address,
        details=details
    )

