from app.models.project import Project
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class PermissionService:
    """Handles group-based project permissions"""

    @staticmethod
    async def can_access_project(user: User, project: Project, db: AsyncSession) -> bool:
        """Check if user can access a project"""
        # Admin has full access
        if user.role == "admin":
            return True
        
        # Owner has full access
        if project.owner_id == user.id:
            return True
        
        # Check if user is a student in this project
        if user.role == "student":
            result = await db.execute(
                select(Project).where(
                    Project.id == project.id
                ).join(Project.students).where(User.id == user.id)
            )
            if result.scalar_one_or_none():
                return True
        
        # Check if user is a supervisor for this project
        if user.role == "supervisor":
            result = await db.execute(
                select(Project).where(
                    Project.id == project.id
                ).join(Project.supervisors).where(User.id == user.id)
            )
            if result.scalar_one_or_none():
                return True
        
        # Public projects are viewable by all
        if project.is_public:
            return True
        
        return False

    @staticmethod
    async def can_modify_project(user: User, project: Project, db: AsyncSession) -> bool:
        """Check if user can modify a project"""
        # Admin has full control
        if user.role == "admin":
            return True
        
        # Owner can modify
        if project.owner_id == user.id:
            return True
        
        # Supervisors can modify
        if user.role == "supervisor":
            result = await db.execute(
                select(Project).where(
                    Project.id == project.id
                ).join(Project.supervisors).where(User.id == user.id)
            )
            if result.scalar_one_or_none():
                return True
        
        return False

    @staticmethod
    async def can_generate_cicd(user: User, project: Project, db: AsyncSession) -> bool:
        """Check if user can trigger AI generation for a project"""
        # Admin can always generate
        if user.role == "admin":
            return True
        
        # Owner can generate
        if project.owner_id == user.id:
            return True
        
        # Students in the project can generate
        if user.role == "student":
            result = await db.execute(
                select(Project).where(
                    Project.id == project.id
                ).join(Project.students).where(User.id == user.id)
            )
            if result.scalar_one_or_none():
                return True
        
        # Supervisors can generate
        if user.role == "supervisor":
            result = await db.execute(
                select(Project).where(
                    Project.id == project.id
                ).join(Project.supervisors).where(User.id == user.id)
            )
            if result.scalar_one_or_none():
                return True
        
        return False
