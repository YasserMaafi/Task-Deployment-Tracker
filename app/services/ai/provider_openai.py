from .base import AIProvider


class OpenAIProvider(AIProvider):

    async def generate(self, prompt: str) -> str:
        # Implementation will come later
        raise NotImplementedError("OpenAI provider not implemented yet")
