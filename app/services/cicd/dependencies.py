from fastapi import Depends
from app.services.ai.dependencies import get_cicd_generator
from app.services.ai.cicd_generator import CICDGenerator
from .cicd_service import CICDService


def get_cicd_service(
    generator: CICDGenerator = Depends(get_cicd_generator)
) -> CICDService:
    return CICDService(generator)
