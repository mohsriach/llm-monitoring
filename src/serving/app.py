import time
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from common.logging import configure_logging
from common.settings import settings
from monitoring.metrics import REQUEST_COUNT, REQUEST_LATENCY_SECONDS, UPSTREAM_ERRORS
from serving.client_vllm import VLLMClient
from serving.schemas import ChatCompletionRequest

configure_logging()

app = FastAPI(title=settings.app_name)
client = VLLMClient()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.get("/metrics")
def metrics() -> JSONResponse:
    return JSONResponse(content=generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/chat/completions")
async def chat_completions(payload: ChatCompletionRequest) -> dict[str, Any]:
    endpoint = "/v1/chat/completions"
    start = time.perf_counter()

    try:
        response = await client.chat_completions(payload.model_dump())
        REQUEST_COUNT.labels(endpoint=endpoint, status="success").inc()
        return response
    except Exception as exc:
        REQUEST_COUNT.labels(endpoint=endpoint, status="error").inc()
        UPSTREAM_ERRORS.inc()
        raise HTTPException(status_code=502, detail=f"Upstream model error: {exc}") from exc
    finally:
        REQUEST_LATENCY_SECONDS.labels(endpoint=endpoint).observe(time.perf_counter() - start)
