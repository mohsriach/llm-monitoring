from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["endpoint", "status"],
)

REQUEST_LATENCY_SECONDS = Histogram(
    "llm_request_latency_seconds",
    "Latency of LLM requests",
    ["endpoint"],
    buckets=(0.1, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0),
)

UPSTREAM_ERRORS = Counter(
    "llm_upstream_errors_total",
    "Total number of upstream model errors",
)
