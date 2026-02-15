import os
import asyncio
import google.generativeai as genai
from .base import AIProvider


class GeminiProvider(AIProvider):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

    async def generate(self, prompt: str) -> str:
        # Use synchronous call in async wrapper for compatibility
        model = genai.GenerativeModel('gemini-pro')
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, model.generate_content, prompt)
        return response.text
