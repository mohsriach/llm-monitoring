import random
import uuid
from datetime import datetime, timedelta, timezone

from monitoring.log_store import clear_logs, init_db, log_inference

BASELINE_PROMPTS = [
    "Summarize this meeting note in 3 bullets.",
    "Rewrite this email to sound professional.",
    "Extract action items from this paragraph.",
    "Draft a concise project status update.",
    "Turn this note into a polite follow-up message.",
]

BASELINE_RESPONSES = [
    "Here are three concise bullets that summarize the update...",
    "Subject: Follow-up on the rollout timeline...",
    "Action items: finalize scope, confirm owners, ship by Friday.",
    "Current status: on track, one dependency at risk.",
]

CURRENT_PROMPTS = [
    "Write a secure Python function for JWT validation.",
    "Explain memory management in C++ with examples.",
    "Design a SQL schema for multi-tenant billing.",
    "Create a Kubernetes deployment manifest with HPA.",
    "Compare Redis pub/sub versus Kafka for event streaming.",
]

CURRENT_RESPONSES = [
    "Use strict audience checks and key rotation for JWT verification.",
    "In C++, RAII helps prevent memory leaks and dangling pointers.",
    "Use tenant_id in all primary access patterns and indexes.",
    "Define resource requests, limits, and autoscaling thresholds.",
]


def _pick(status: str, prompts: list, responses: list) -> tuple:
    prompt = random.choice(prompts)
    if status == "success":
        response = random.choice(responses)
        return prompt, response, None
    return prompt, "", "synthetic upstream timeout"


def seed_synthetic_drift_data(
    baseline_size: int = 300,
    current_size: int = 100,
    baseline_error_rate: float = 0.01,
    current_error_rate: float = 0.08,
    baseline_latency_range: tuple = (120.0, 300.0),
    current_latency_range: tuple = (250.0, 700.0),
    clear_existing: bool = True,
    seed: int = 42,
) -> dict:
    random.seed(seed)
    init_db()

    if clear_existing:
        clear_logs()

    total = baseline_size + current_size
    start_time = datetime.now(timezone.utc) - timedelta(minutes=total)

    inserted = 0
    for i in range(total):
        is_baseline = i < baseline_size
        error_rate = baseline_error_rate if is_baseline else current_error_rate
        latency_range = baseline_latency_range if is_baseline else current_latency_range
        prompts = BASELINE_PROMPTS if is_baseline else CURRENT_PROMPTS
        responses = BASELINE_RESPONSES if is_baseline else CURRENT_RESPONSES

        status = "error" if random.random() < error_rate else "success"
        prompt, response, error_message = _pick(status, prompts, responses)
        created_at = (start_time + timedelta(minutes=i)).isoformat()
        latency_ms = random.uniform(*latency_range)

        log_inference(
            {
                "id": str(uuid.uuid4()),
                "created_at": created_at,
                "endpoint": "/v1/chat/completions",
                "model": "Qwen/Qwen2.5-3B-Instruct",
                "status": status,
                "latency_ms": latency_ms,
                "prompt_text": prompt,
                "response_text": response,
                "prompt_chars": len(prompt),
                "response_chars": len(response),
                "error_message": error_message,
            }
        )
        inserted += 1

    return {
        "inserted": inserted,
        "baseline_size": baseline_size,
        "current_size": current_size,
        "baseline_error_rate": baseline_error_rate,
        "current_error_rate": current_error_rate,
    }
