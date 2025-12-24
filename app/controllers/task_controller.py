"""
Task Controller
Handles task management logic
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


class TaskController:
    """Task management business logic"""
    
    @staticmethod
    def get_tasks(
        company_id: int,
        current_user: User,
        db: Session,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[int] = None,
        task_type: Optional[str] = None
    ) -> List[Task]:
        """Get all tasks in company"""
        query = db.query(Task).filter(Task.company_id == company_id)
        
        if search:
            query = query.filter(
                (Task.title.contains(search)) |
                (Task.description.contains(search))
            )
        
        if status:
            query = query.filter(Task.status == status)
        
        if priority:
            query = query.filter(Task.priority == priority)
        
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        
        if task_type:
            query = query.filter(Task.task_type == task_type)
        
        tasks = query.order_by(Task.due_date.asc().nullslast()).all()
        return tasks
    
    @staticmethod
    def create_task(
        company_id: int,
        task_data: TaskCreate,
        current_user: User,
        db: Session
    ) -> Task:
        """Create new task"""
        new_task = Task(
            company_id=company_id,
            **task_data.model_dump(),
            created_by=current_user.id
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        return new_task
    
    @staticmethod
    def get_task(
        task_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ) -> Task:
        """Get task by ID"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.company_id == company_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return task
    
    @staticmethod
    def update_task(
        task_id: int,
        company_id: int,
        task_data: TaskUpdate,
        current_user: User,
        db: Session
    ) -> Task:
        """Update task"""
        task = TaskController.get_task(task_id, company_id, current_user, db)
        
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        
        # Auto-set completed_at if status changed to completed
        if update_data.get("status") == "completed" and not task.completed_at:
            task.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return task
    
    @staticmethod
    def complete_task(
        task_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ) -> Task:
        """Mark task as completed"""
        task = TaskController.get_task(task_id, company_id, current_user, db)
        
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return task
    
    @staticmethod
    def delete_task(
        task_id: int,
        company_id: int,
        current_user: User,
        db: Session
    ):
        """Delete task"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.company_id == company_id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        db.delete(task)
        db.commit()
    
    @staticmethod
    def get_task_stats(company_id: int, db: Session) -> dict:
        """Get task statistics for company"""
        from sqlalchemy import func
        
        total = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id
        ).scalar()
        
        by_status = {}
        statuses = ["pending", "in_progress", "completed", "cancelled"]
        for s in statuses:
            count = db.query(func.count(Task.id)).filter(
                Task.company_id == company_id,
                Task.status == s
            ).scalar()
            by_status[s] = count or 0
        
        overdue = db.query(func.count(Task.id)).filter(
            Task.company_id == company_id,
            Task.status.in_(["pending", "in_progress"]),
            Task.due_date < datetime.utcnow()
        ).scalar()
        
        return {
            "total_tasks": total or 0,
            "by_status": by_status,
            "overdue_tasks": overdue or 0
        }

