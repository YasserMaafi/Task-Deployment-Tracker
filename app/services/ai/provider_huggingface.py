import os
import httpx
from .base import AIProvider


class HuggingFaceProvider(AIProvider):

    def __init__(self):
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable not set")
        
        # Using Qwen2.5-Coder - actively maintained for code generation
        self.api_url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"

    async def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2000,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "")
            
            raise ValueError("No valid response from Hugging Face API")
