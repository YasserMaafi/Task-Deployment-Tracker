from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_session
from app.services.cicd.dependencies import get_cicd_service
from app.services.cicd.cicd_service import CICDService
from app.models.project import Project
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.ai_generation import AIGenerationResponse

router = APIRouter(prefix="/projects", tags=["CI/CD"])


@router.post("/{project_id}/generate-cicd", response_model=AIGenerationResponse)
async def generate_cicd(
    project_id: int,
    db: AsyncSession = Depends(get_session),
    cicd_service: CICDService = Depends(get_cicd_service),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a CI/CD pipeline for a project.
    
    - **project_id**: ID of the project to generate pipeline for
    - Requires: Project owner or admin role
    - Returns: AI generation record with YAML output
    """
    # 1️⃣ Fetch project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    try:
        # 2️⃣ Delegate to CICDService
        ai_record = await cicd_service.generate_pipeline(project, current_user, db)
        return ai_record

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CI/CD pipeline: {str(e)}"
        )
