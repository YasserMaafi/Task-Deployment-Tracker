from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_session
from app.models.project import Project
from app.models.user import User
from app.models.project_feedback import ProjectFeedback
from app.core.dependencies import get_current_user
from app.services.permissions import PermissionService
from app.schemas.project import ProjectMemberAdd, ProjectMemberRemove, FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/projects", tags=["Project Management"])


@router.post("/{project_id}/students")
async def add_student_to_project(
    project_id: int,
    member_data: ProjectMemberAdd,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Add a student to a project (admin, owner, or supervisor only)"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only admin, owner, or supervisors can add students
    can_modify = await PermissionService.can_modify_project(current_user, project, db)
    if not can_modify:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get the student user
    student_result = await db.execute(select(User).where(User.id == member_data.user_id))
    student = student_result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="User not found")
    
    if student.role != "student":
        raise HTTPException(status_code=400, detail="User must have student role")
    
    # Add student to project
    if student not in project.students:
        project.students.append(student)
        await db.commit()
    
    return {"message": f"Student {student.username} added to project"}


@router.delete("/{project_id}/students/{user_id}")
async def remove_student_from_project(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Remove a student from a project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    can_modify = await PermissionService.can_modify_project(current_user, project, db)
    if not can_modify:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    student_result = await db.execute(select(User).where(User.id == user_id))
    student = student_result.scalar_one_or_none()
    
    if student and student in project.students:
        project.students.remove(student)
        await db.commit()
    
    return {"message": "Student removed from project"}


@router.post("/{project_id}/supervisors")
async def add_supervisor_to_project(
    project_id: int,
    member_data: ProjectMemberAdd,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Add a supervisor to a project (admin or owner only)"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only admin or owner can add supervisors
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    supervisor_result = await db.execute(select(User).where(User.id == member_data.user_id))
    supervisor = supervisor_result.scalar_one_or_none()
    
    if not supervisor:
        raise HTTPException(status_code=404, detail="User not found")
    
    if supervisor.role != "supervisor":
        raise HTTPException(status_code=400, detail="User must have supervisor role")
    
    if supervisor not in project.supervisors:
        project.supervisors.append(supervisor)
        await db.commit()
    
    return {"message": f"Supervisor {supervisor.username} added to project"}


@router.delete("/{project_id}/supervisors/{user_id}")
async def remove_supervisor_from_project(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Remove a supervisor from a project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    supervisor_result = await db.execute(select(User).where(User.id == user_id))
    supervisor = supervisor_result.scalar_one_or_none()
    
    if supervisor and supervisor in project.supervisors:
        project.supervisors.remove(supervisor)
        await db.commit()
    
    return {"message": "Supervisor removed from project"}


@router.post("/{project_id}/feedback", response_model=FeedbackResponse)
async def create_feedback(
    project_id: int,
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create feedback for a project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    can_access = await PermissionService.can_access_project(current_user, project, db)
    if not can_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    feedback = ProjectFeedback(
        project_id=project_id,
        user_id=current_user.id,
        feedback_type=feedback_data.feedback_type,
        content=feedback_data.content
    )
    
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    
    return feedback


@router.get("/{project_id}/feedback")
async def get_project_feedback(
    project_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get all feedback for a project"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    can_access = await PermissionService.can_access_project(current_user, project, db)
    if not can_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    feedback_result = await db.execute(
        select(ProjectFeedback).where(ProjectFeedback.project_id == project_id)
    )
    feedback_list = feedback_result.scalars().all()
    
    return feedback_list
