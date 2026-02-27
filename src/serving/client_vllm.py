import httpx

from common.settings import settings


class VLLMClient:
    def __init__(self) -> None:
        self.base_url = settings.vllm_base_url
        self.timeout = settings.request_timeout_seconds

    async def chat_completions(self, payload: dict) -> dict:
        url = f"{self.base_url}/chat/completions"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
