import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from common.logging import configure_logging
from common.settings import settings
from monitoring.log_store import init_db, log_inference
from monitoring.metrics import REQUEST_COUNT, REQUEST_LATENCY_SECONDS, UPSTREAM_ERRORS
from serving.client_vllm import VLLMClient
from serving.schemas import ChatCompletionRequest

configure_logging()

app = FastAPI(title=settings.app_name)
client = VLLMClient()


def _flatten_response_text(response_payload: Dict[str, Any]) -> str:
    texts: List[str] = []
    for choice in response_payload.get("choices", []) or []:
        message = choice.get("message") or {}
        if isinstance(message, dict) and message.get("content"):
            texts.append(str(message.get("content")))
            continue
        if choice.get("text"):
            texts.append(str(choice.get("text")))
    return "\n".join(texts)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.get("/metrics")
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/chat/completions")
async def chat_completions(payload: ChatCompletionRequest) -> Dict[str, Any]:
    endpoint = "/v1/chat/completions"
    request_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()

    prompt_text = "\n".join([m.content for m in payload.messages])
    response_text = ""
    status = "success"
    error_message = None

    try:
        response = await client.chat_completions(payload.model_dump())
        response_text = _flatten_response_text(response)
        REQUEST_COUNT.labels(endpoint=endpoint, status="success").inc()
        return response
    except Exception as exc:
        status = "error"
        error_message = str(exc)
        REQUEST_COUNT.labels(endpoint=endpoint, status="error").inc()
        UPSTREAM_ERRORS.inc()
        raise HTTPException(status_code=502, detail="Upstream model error") from exc
    finally:
        latency_ms = (time.perf_counter() - start) * 1000.0
        REQUEST_LATENCY_SECONDS.labels(endpoint=endpoint).observe(latency_ms / 1000.0)
        log_inference(
            {
                "id": request_id,
                "created_at": created_at,
                "endpoint": endpoint,
                "model": payload.model,
                "status": status,
                "latency_ms": latency_ms,
                "prompt_text": prompt_text,
                "response_text": response_text,
                "prompt_chars": len(prompt_text),
                "response_chars": len(response_text),
                "error_message": error_message,
            }
        )
