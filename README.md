# llm-observatory

Production-style LLM observability starter project.

## What Is Implemented

### Milestone 1
- FastAPI wrapper endpoint for chat completions
- Proxy client to open-source model server (`vLLM` OpenAI-compatible API)
- Prometheus metrics (`/metrics`)
- Docker Compose stack (API + Prometheus + Grafana)

### Milestone 2
- Persistent inference logging to SQLite (`data/monitoring/requests.db`)
- Drift analysis job for prompts/outputs + latency/error regression checks
- Drift report JSON output (`reports/drift/latest.json`)
- Starter Grafana dashboard JSON (`dashboards/grafana/llm_observatory_overview.json`)

## Practical Workflow
1. Run model server (`vLLM`) and API wrapper.
2. Send traffic to `POST /v1/chat/completions`.
3. API logs every request/response/latency/status to SQLite.
4. Run `make drift-check` to compare baseline vs current windows.
5. Inspect `reports/drift/latest.json` and monitor Prometheus/Grafana panels.

## Quick Start (Local API only)
1. Create env file:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Run API:
   ```bash
   make run
   ```
4. Check health:
   ```bash
   curl http://localhost:8080/health
   ```

## Send a Test Request
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-3B-Instruct",
    "messages": [{"role":"user","content":"Give me 3 ideas to monitor LLM quality."}],
    "temperature": 0.2,
    "max_tokens": 120
  }'
```

## Run Drift Check
```bash
make drift-check
```
This writes a report to `reports/drift/latest.json`.

## Run Full Stack
```bash
docker compose up --build
```
- API: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Start vLLM (GPU host)
The `vllm` service is under Docker profile `gpu`:
```bash
docker compose --profile gpu up --build
```

## Next Milestones
- Safety checks (PII, toxicity)
- Eval pipeline with golden datasets
- Alerting and canary rollout
