import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    vllm_base_url: str
    request_timeout_seconds: int


settings = Settings(
    app_name=os.getenv("APP_NAME", "llm-observatory"),
    app_env=os.getenv("APP_ENV", "local"),
    vllm_base_url=os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
    request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "60")),
)
