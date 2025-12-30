"""
Task Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate
from app.controllers.task_controller import TaskController
from app.utils.dependencies import get_current_active_user
from app.utils.helpers import success_response
from app.utils.permissions import has_permission
from app.models.user import User

router = APIRouter()


@router.get("/{company_id}/tasks")
async def get_tasks(
    company_id: int = Path(..., description="Company ID"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    task_type: Optional[str] = Query(None, description="Filter by type"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all tasks in company"""
    try:
        tasks = TaskController.get_tasks(
            company_id, current_user, db, search, status, priority, assigned_to, task_type
        )
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_tasks = tasks[start:end]
        
        total = len(tasks)
        pages = (total + per_page - 1) // per_page
        
        return {
            "success": True,
            "data": [task.to_dict(include_relations=True) for task in paginated_tasks],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages
            },
            "message": "Tasks fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{company_id}/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    company_id: int = Path(..., description="Company ID"),
    task_data: TaskCreate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new task
    
    Path Parameters:
    - **company_id**: Company ID
    
    Requires: JWT token, Permission to create tasks
    """
    # Check permission to create task
    if not has_permission(current_user, "task", "create", company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: create task"
        )
    
    try:
        task = TaskController.create_task(company_id, task_data, current_user, db)
        return success_response(
            data=task.to_dict(include_relations=True),
            message="Task created successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================
# IMPORTANT: Static routes MUST come before dynamic {task_id} routes
# ============================================

@router.get("/{company_id}/tasks/automation-stats")
async def get_task_automation_stats_early(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get task automation statistics"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from app.models.task import Task
    
    try:
        today = datetime.utcnow().date()
        
        # Total tasks
        total = db.query(func.count(Task.id)).filter(Task.company_id == company_id).scalar() or 0
        
        # Pending tasks
        pending = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id,
            Task.status == "pending"
        ).scalar() or 0
        
        # Overdue tasks
        overdue = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id,
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date < today
        ).scalar() or 0
        
        # Completed today
        completed_today = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id,
            Task.status == "completed",
            func.date(Task.updated_at) == today
        ).scalar() or 0
        
        # By priority
        by_priority = {}
        for priority in ["urgent", "high", "medium", "low"]:
            count = db.query(func.count(Task.id)).filter(
                Task.company_id == company_id,
                Task.priority == priority,
                Task.status.in_(["pending", "in_progress"])
            ).scalar() or 0
            by_priority[priority] = count
        
        return success_response(
            data={
                "total_tasks": total,
                "pending_tasks": pending,
                "overdue_tasks": overdue,
                "completed_today": completed_today,
                "by_priority": by_priority
            },
            message="Task automation stats fetched"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching stats: {str(e)}"
        )


@router.get("/{company_id}/tasks/overdue")
async def get_overdue_tasks_early(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overdue tasks"""
    from datetime import datetime
    from app.models.task import Task
    
    try:
        today = datetime.utcnow().date()
        
        overdue_tasks = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date < today
        ).order_by(Task.due_date.asc()).all()
        
        result = []
        for task in overdue_tasks:
            days_overdue = (today - task.due_date).days if task.due_date else 0
            result.append({
                "id": task.id,
                "title": task.title,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "days_overdue": days_overdue,
                "assigned_to": task.assigned_user.email if task.assigned_user else None
            })
        
        return success_response(
            data={"overdue_tasks": result, "count": len(result)},
            message=f"Found {len(result)} overdue tasks"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching overdue tasks: {str(e)}"
        )


@router.post("/{company_id}/tasks/escalate-overdue")
async def escalate_overdue_tasks_early(
    company_id: int = Path(..., description="Company ID"),
    escalation_days: int = Query(3, ge=1, le=14, description="Days overdue to trigger escalation"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Escalate overdue tasks"""
    from datetime import datetime, timedelta
    from app.models.task import Task
    
    try:
        today = datetime.utcnow().date()
        threshold = today - timedelta(days=escalation_days)
        
        tasks_to_escalate = db.query(Task).filter(
            Task.company_id == company_id,
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date <= threshold,
            Task.priority != "urgent"
        ).all()
        
        escalated = 0
        for task in tasks_to_escalate:
            if task.priority == "low":
                task.priority = "medium"
            elif task.priority == "medium":
                task.priority = "high"
            elif task.priority == "high":
                task.priority = "urgent"
            escalated += 1
        
        db.commit()
        
        return success_response(
            data={"escalated": escalated},
            message=f"Escalated {escalated} tasks"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error escalating tasks: {str(e)}"
        )


@router.post("/{company_id}/tasks/auto-create-for-leads")
async def auto_create_tasks_for_leads_early(
    company_id: int = Path(..., description="Company ID"),
    days_since_creation: int = Query(7, ge=1, le=30, description="Days since lead creation"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Auto-create follow-up tasks for leads without recent tasks"""
    from datetime import datetime, timedelta
    from app.models.lead import Lead
    from app.models.task import Task
    
    try:
        threshold = datetime.utcnow() - timedelta(days=days_since_creation)
        
        # Find leads without recent tasks
        leads = db.query(Lead).filter(
            Lead.company_id == company_id,
            Lead.status.in_(["new", "contacted"]),
            Lead.created_at <= threshold
        ).all()
        
        tasks_created = 0
        for lead in leads:
            # Check if lead has recent task
            recent_task = db.query(Task).filter(
                Task.lead_id == lead.id,
                Task.created_at >= threshold
            ).first()
            
            if not recent_task:
                new_task = Task(
                    company_id=company_id,
                    lead_id=lead.id,
                    title=f"Follow up - {lead.lead_name or lead.first_name}",
                    description=f"Auto-created follow-up task for lead",
                    task_type="follow_up",
                    priority="medium",
                    status="pending",
                    due_date=(datetime.utcnow() + timedelta(days=3)).date(),
                    assigned_to=lead.assigned_to or current_user.id
                )
                db.add(new_task)
                tasks_created += 1
        
        db.commit()
        
        return success_response(
            data={"tasks_created": tasks_created},
            message=f"Created {tasks_created} follow-up tasks"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating tasks: {str(e)}"
        )


# ============================================
# Dynamic routes with {task_id} parameter
# ============================================

@router.get("/{company_id}/tasks/{task_id}")
async def get_task(
    company_id: int = Path(..., description="Company ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get task details"""
    try:
        task = TaskController.get_task(task_id, company_id, current_user, db)
        return success_response(
            data=task.to_dict(include_relations=True),
            message="Task details fetched successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/tasks/{task_id}")
async def update_task(
    company_id: int = Path(..., description="Company ID"),
    task_id: int = Path(..., description="Task ID"),
    task_data: TaskUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update task
    
    Path Parameters:
    - **company_id**: Company ID
    - **task_id**: Task ID
    
    Requires: JWT token, Permission to update tasks
    """
    # Check permission to update task
    if not has_permission(current_user, "task", "update", company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: update task"
        )
    
    try:
        task = TaskController.update_task(task_id, company_id, task_data, current_user, db)
        return success_response(
            data=task.to_dict(include_relations=True),
            message="Task updated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{company_id}/tasks/{task_id}/complete")
async def complete_task(
    company_id: int = Path(..., description="Company ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark task as completed"""
    try:
        task = TaskController.complete_task(task_id, company_id, current_user, db)
        return success_response(
            data=task.to_dict(include_relations=True),
            message="Task marked as completed"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{company_id}/tasks/{task_id}")
async def delete_task(
    company_id: int = Path(..., description="Company ID"),
    task_id: int = Path(..., description="Task ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete task
    
    Path Parameters:
    - **company_id**: Company ID
    - **task_id**: Task ID
    
    Requires: JWT token, Permission to delete tasks
    """
    # Check permission to delete task
    if not has_permission(current_user, "task", "delete", company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: delete task"
        )
    """
    Delete task
    
    Path Parameters:
    - **company_id**: Company ID
    - **task_id**: Task ID
    
    Requires: JWT token, Permission to delete tasks
    """
    # Check permission to delete task
    if not has_permission(current_user, "task", "delete", company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: delete task"
        )
    
    try:
        TaskController.delete_task(task_id, company_id, current_user, db)
        return success_response(
            data={},
            message="Task deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{company_id}/tasks-stats")
async def get_task_stats(
    company_id: int = Path(..., description="Company ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get task statistics"""
    try:
        stats = TaskController.get_task_stats(company_id, db)
        return success_response(
            data=stats,
            message="Task statistics fetched successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

