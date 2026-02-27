from monitoring.drift import compute_drift_report


def _row(i, prompt, response, status="success", latency=100):
    return {
        "id": str(i),
        "created_at": "2026-01-01T00:{:02d}:00Z".format(i % 60),
        "status": status,
        "prompt_text": prompt,
        "response_text": response,
        "latency_ms": latency,
    }


def test_drift_report_insufficient_data():
    report = compute_drift_report([], baseline_size=10, current_size=5)
    assert report["status"] == "insufficient_data"


def test_drift_report_generates_metrics():
    baseline = [_row(i, "weather today", "mild and sunny", latency=120) for i in range(40)]
    current = [_row(i + 40, "stock market now", "high volatility", latency=220) for i in range(20)]
    report = compute_drift_report(baseline + current, baseline_size=40, current_size=20)

    assert report["status"] == "ok"
    assert "metrics" in report
    assert "prompt_jsd" in report["metrics"]
