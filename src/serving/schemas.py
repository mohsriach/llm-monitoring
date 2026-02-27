from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="Qwen/Qwen2.5-3B-Instruct")
    messages: list[ChatMessage]
    temperature: float = 0.2
    max_tokens: int = 256


class ChatCompletionResponse(BaseModel):
    id: Optional[str] = None
    object: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: list[dict[str, Any]] = Field(default_factory=list)
    usage: Optional[dict[str, Any]] = None
