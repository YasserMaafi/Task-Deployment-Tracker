from fastapi import Depends
from .provider_gemini import GeminiProvider
from .base import AIProvider
from .cicd_generator import CICDGenerator


def get_ai_provider() -> AIProvider:
    return GeminiProvider()


def get_cicd_generator(
    provider: AIProvider = Depends(get_ai_provider)
) -> CICDGenerator:
    return CICDGenerator(provider)
