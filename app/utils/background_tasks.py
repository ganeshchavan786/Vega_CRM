"""
Background Tasks Manager
Handles async background task execution for the CRM application
"""

from fastapi import BackgroundTasks
from typing import Callable, Any, Dict, List, Optional
from datetime import datetime
import asyncio
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """
    Manages background tasks with retry logic and task tracking
    """
    
    def __init__(self):
        self.task_queue: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.failed_tasks: List[Dict] = []
        self.max_queue_size = settings.TASK_QUEUE_SIZE
        self.retry_count = settings.TASK_RETRY_COUNT
        self.retry_delay = settings.TASK_RETRY_DELAY
    
    def add_task(
        self,
        background_tasks: BackgroundTasks,
        func: Callable,
        *args,
        task_name: str = None,
        **kwargs
    ):
        """Add a task to the background queue"""
        if not settings.BACKGROUND_TASK_ENABLED:
            logger.warning("Background tasks are disabled")
            return
        
        task_info = {
            "name": task_name or func.__name__,
            "created_at": datetime.utcnow().isoformat(),
            "status": "queued",
            "args": str(args),
            "kwargs": str(kwargs)
        }
        
        if len(self.task_queue) >= self.max_queue_size:
            logger.warning(f"Task queue full ({self.max_queue_size}), dropping oldest task")
            self.task_queue.pop(0)
        
        self.task_queue.append(task_info)
        background_tasks.add_task(self._execute_task, func, task_info, *args, **kwargs)
        logger.info(f"Task '{task_info['name']}' added to queue")
    
    async def _execute_task(
        self,
        func: Callable,
        task_info: Dict,
        *args,
        **kwargs
    ):
        """Execute task with retry logic"""
        task_info["status"] = "running"
        task_info["started_at"] = datetime.utcnow().isoformat()
        
        for attempt in range(self.retry_count):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                task_info["status"] = "completed"
                task_info["completed_at"] = datetime.utcnow().isoformat()
                task_info["result"] = str(result)[:200] if result else None
                
                self.task_queue.remove(task_info)
                self.completed_tasks.append(task_info)
                
                # Keep only last 100 completed tasks
                if len(self.completed_tasks) > 100:
                    self.completed_tasks = self.completed_tasks[-100:]
                
                logger.info(f"Task '{task_info['name']}' completed successfully")
                return result
                
            except Exception as e:
                logger.error(f"Task '{task_info['name']}' failed (attempt {attempt + 1}): {str(e)}")
                
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    task_info["status"] = "failed"
                    task_info["error"] = str(e)
                    task_info["failed_at"] = datetime.utcnow().isoformat()
                    
                    if task_info in self.task_queue:
                        self.task_queue.remove(task_info)
                    self.failed_tasks.append(task_info)
                    
                    # Keep only last 50 failed tasks
                    if len(self.failed_tasks) > 50:
                        self.failed_tasks = self.failed_tasks[-50:]
    
    def get_status(self) -> Dict:
        """Get current task queue status"""
        return {
            "enabled": settings.BACKGROUND_TASK_ENABLED,
            "queued": len(self.task_queue),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "max_queue_size": self.max_queue_size,
            "recent_tasks": self.task_queue[-10:] if self.task_queue else []
        }


# Global task manager instance
task_manager = BackgroundTaskManager()


# ============================================
# Common Background Task Functions
# ============================================

async def send_email_task(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
):
    """Background task to send email"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, email not sent")
        return {"status": "skipped", "reason": "SMTP not configured"}
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        
        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
        
        logger.info(f"Email sent to {to_email}")
        return {"status": "sent", "to": to_email}
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise


async def log_activity_task(
    company_id: int,
    activity_type: str,
    title: str,
    description: str,
    user_id: int,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None
):
    """Background task to log activity"""
    from app.database import SessionLocal
    from app.models.activity import Activity
    
    try:
        db = SessionLocal()
        activity = Activity(
            company_id=company_id,
            activity_type=activity_type,
            title=title,
            description=description,
            user_id=user_id,
            activity_date=datetime.utcnow()
        )
        
        if entity_type == "lead":
            activity.lead_id = entity_id
        elif entity_type == "deal":
            activity.deal_id = entity_id
        elif entity_type == "customer":
            activity.customer_id = entity_id
        elif entity_type == "contact":
            activity.contact_id = entity_id
        
        db.add(activity)
        db.commit()
        db.close()
        
        logger.info(f"Activity logged: {title}")
        return {"status": "logged", "activity_type": activity_type}
    except Exception as e:
        logger.error(f"Failed to log activity: {str(e)}")
        raise


async def update_lead_score_task(lead_id: int, company_id: int):
    """Background task to recalculate lead score"""
    from app.database import SessionLocal
    from app.utils.lead_scoring import LeadScoringAlgorithm
    
    try:
        db = SessionLocal()
        scorer = LeadScoringAlgorithm(db)
        new_score = scorer.calculate_score(lead_id)
        db.close()
        
        logger.info(f"Lead {lead_id} score updated to {new_score}")
        return {"status": "updated", "lead_id": lead_id, "new_score": new_score}
    except Exception as e:
        logger.error(f"Failed to update lead score: {str(e)}")
        raise


async def cleanup_old_data_task(company_id: int, days: int = 90):
    """Background task to cleanup old audit logs and activities"""
    from app.database import SessionLocal
    from app.models.audit_log import AuditLog
    from datetime import timedelta
    
    try:
        db = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = db.query(AuditLog).filter(
            AuditLog.company_id == company_id,
            AuditLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        db.close()
        
        logger.info(f"Cleaned up {deleted} old audit logs for company {company_id}")
        return {"status": "cleaned", "deleted_count": deleted}
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {str(e)}")
        raise
