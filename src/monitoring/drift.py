import math
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", (text or "").lower())


def _distribution(texts: List[str]) -> Dict[str, float]:
    counts = Counter()
    for text in texts:
        counts.update(_tokenize(text))

    total = float(sum(counts.values()))
    if total == 0:
        return {}
    return {k: v / total for k, v in counts.items()}


def _js_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
    keys = set(p.keys()) | set(q.keys())
    if not keys:
        return 0.0

    def _kld(a: Dict[str, float], b: Dict[str, float]) -> float:
        value = 0.0
        for key in keys:
            a_i = a.get(key, 0.0)
            b_i = b.get(key, 0.0)
            if a_i > 0 and b_i > 0:
                value += a_i * math.log(a_i / b_i, 2)
        return value

    m = {k: 0.5 * (p.get(k, 0.0) + q.get(k, 0.0)) for k in keys}
    return 0.5 * _kld(p, m) + 0.5 * _kld(q, m)


def _mean(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def compute_drift_report(logs: List[Dict], baseline_size: int = 300, current_size: int = 100) -> Dict:
    ordered = sorted(logs, key=lambda row: row.get("created_at", ""))
    if len(ordered) < baseline_size + current_size:
        return {
            "status": "insufficient_data",
            "message": "Need at least baseline_size + current_size log rows",
            "required": baseline_size + current_size,
            "available": len(ordered),
        }

    baseline = ordered[-(baseline_size + current_size) : -current_size]
    current = ordered[-current_size:]

    baseline_prompts = [row.get("prompt_text", "") for row in baseline if row.get("status") == "success"]
    current_prompts = [row.get("prompt_text", "") for row in current if row.get("status") == "success"]

    baseline_outputs = [row.get("response_text", "") for row in baseline if row.get("status") == "success"]
    current_outputs = [row.get("response_text", "") for row in current if row.get("status") == "success"]

    prompt_jsd = _js_divergence(_distribution(baseline_prompts), _distribution(current_prompts))
    output_jsd = _js_divergence(_distribution(baseline_outputs), _distribution(current_outputs))

    baseline_latency = [float(row.get("latency_ms") or 0.0) for row in baseline]
    current_latency = [float(row.get("latency_ms") or 0.0) for row in current]
    baseline_errors = len([row for row in baseline if row.get("status") != "success"])
    current_errors = len([row for row in current if row.get("status") != "success"])

    latency_shift_pct = 0.0
    if _mean(baseline_latency) > 0:
        latency_shift_pct = ((_mean(current_latency) - _mean(baseline_latency)) / _mean(baseline_latency)) * 100

    baseline_error_rate = baseline_errors / float(len(baseline) or 1)
    current_error_rate = current_errors / float(len(current) or 1)

    severity = "low"
    alerts = []

    if prompt_jsd > 0.12:
        alerts.append("prompt_drift")
    if output_jsd > 0.12:
        alerts.append("output_drift")
    if latency_shift_pct > 35:
        alerts.append("latency_regression")
    if current_error_rate - baseline_error_rate > 0.05:
        alerts.append("error_rate_regression")

    if len(alerts) >= 3:
        severity = "high"
    elif len(alerts) >= 1:
        severity = "medium"

    return {
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "window": {
            "baseline_size": baseline_size,
            "current_size": current_size,
        },
        "metrics": {
            "prompt_jsd": round(prompt_jsd, 4),
            "output_jsd": round(output_jsd, 4),
            "baseline_avg_latency_ms": round(_mean(baseline_latency), 2),
            "current_avg_latency_ms": round(_mean(current_latency), 2),
            "latency_shift_pct": round(latency_shift_pct, 2),
            "baseline_error_rate": round(baseline_error_rate, 4),
            "current_error_rate": round(current_error_rate, 4),
        },
        "alerts": alerts,
        "severity": severity,
    }
