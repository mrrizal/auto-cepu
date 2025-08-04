import httpx
from typing import Optional


class CodeReviewLLM:
    def __init__(self, model: str = "deepseek-coder:6.7b-instruct"):
        self.model = model
        self.base_url = "http://localhost:11434/api/generate"

    async def review(self, prompt: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                url=self.base_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": 0.1,
                    "top_k": 20,
                    "top_p": 0.8,
                    "repeat_penalty": 1.2,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()
