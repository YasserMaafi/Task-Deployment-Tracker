from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.database import get_session
from app.models.task import Task, TaskStatus, AssignmentStatus
from app.models.project import Project
from app.models.user import User
from app.models.activity import TaskActivity
from app.core.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None

async def log_activity(db: AsyncSession, task_id: int, user_id: int, action: str, details: str = None):
    activity = TaskActivity(
        task_id=task_id,
        user_id=user_id,
        action=action,
        details=details
    )
    db.add(activity)
    await db.commit()

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if project exists
    result = await db.execute(select(Project).where(Project.id == task_data.project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only project owner or admin can create tasks
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only project owner can create tasks")
    
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id,
        creator_id=current_user.id,
        assignee_id=task_data.assignee_id,
        assignment_status=AssignmentStatus.PENDING if task_data.assignee_id else None
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    await log_activity(db, new_task.id, current_user.id, "created", f"Task created")
    if task_data.assignee_id:
        await log_activity(db, new_task.id, current_user.id, "assigned", f"Assigned to user {task_data.assignee_id}")
    
    return new_task

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check project visibility
    if not task.project.is_public:
        if task.project.owner_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Cannot view tasks in private project")
    
    return task

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Can update if: task creator, project owner, assignee, or admin
    can_update = (
        task.creator_id == current_user.id or
        task.project.owner_id == current_user.id or
        task.assignee_id == current_user.id or
        current_user.role == "admin"
    )
    
    if not can_update:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    # Only project owner or admin can change assignee
    if task_data.assignee_id is not None:
        if task.project.owner_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only project owner can change assignee")
        task.assignee_id = task_data.assignee_id
        task.assignment_status = AssignmentStatus.PENDING if task_data.assignee_id else None
        await log_activity(db, task_id, current_user.id, "reassigned", f"Reassigned to user {task_data.assignee_id}")
    
    if task_data.title:
        task.title = task_data.title
        await log_activity(db, task_id, current_user.id, "updated", "Title updated")
    if task_data.description:
        task.description = task_data.description
        await log_activity(db, task_id, current_user.id, "updated", "Description updated")
    if task_data.status:
        old_status = task.status
        task.status = task_data.status
        await log_activity(db, task_id, current_user.id, "status_changed", f"Status changed from {old_status.value} to {task_data.status.value}")
    
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Can delete if: project owner or admin (NOT task creator)
    can_delete = (
        task.project.owner_id == current_user.id or
        current_user.role == "admin"
    )
    
    if not can_delete:
        raise HTTPException(status_code=403, detail="Only project owner or admin can delete tasks")
    
    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully"}


@router.post("/tasks/{task_id}/accept")
async def accept_assignment(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not assigned to this task")
    
    if task.assignment_status != AssignmentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Assignment already processed")
    
    task.assignment_status = AssignmentStatus.ACCEPTED
    await db.commit()
    await log_activity(db, task_id, current_user.id, "accepted", "Accepted task assignment")
    
    return {"message": "Assignment accepted"}

@router.post("/tasks/{task_id}/reject")
async def reject_assignment(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not assigned to this task")
    
    if task.assignment_status != AssignmentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Assignment already processed")
    
    task.assignment_status = AssignmentStatus.REJECTED
    task.assignee_id = None
    await db.commit()
    await log_activity(db, task_id, current_user.id, "rejected", "Rejected task assignment")
    
    return {"message": "Assignment rejected"}

@router.post("/tasks/{task_id}/start")
async def start_task(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not assigned to this task")
    
    if task.assignment_status != AssignmentStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Must accept assignment first")
    
    if task.working_user_id:
        raise HTTPException(status_code=400, detail="Task already being worked on")
    
    task.working_user_id = current_user.id
    task.status = TaskStatus.IN_PROGRESS
    await db.commit()
    await log_activity(db, task_id, current_user.id, "started", "Started working on task")
    
    return {"message": "Task started", "working_user_id": current_user.id}

@router.get("/tasks/{task_id}/activities")
async def get_task_activities(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(TaskActivity).where(TaskActivity.task_id == task_id).order_by(TaskActivity.created_at.desc())
    )
    activities = result.scalars().all()
    return activities
