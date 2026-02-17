from fastapi import Depends
from .provider_stub import StubProvider
from .base import AIProvider
from .cicd_generator import CICDGenerator


def get_ai_provider() -> AIProvider:
    return StubProvider()


def get_cicd_generator(
    provider: AIProvider = Depends(get_ai_provider)
) -> CICDGenerator:
    return CICDGenerator(provider)
