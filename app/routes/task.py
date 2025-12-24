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
    """Create new task"""
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
    """Update task"""
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
    """Delete task"""
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

