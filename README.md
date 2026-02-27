# llm-observatory

Production-style LLM observability starter project.

## Milestone 1
- FastAPI wrapper endpoint for chat completions
- Proxy client to open-source model server (`vLLM` OpenAI-compatible API)
- Prometheus metrics (`/metrics`)
- Docker Compose stack (API + Prometheus + Grafana)

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
- Drift detection on prompt/output embeddings
- Safety checks (PII, toxicity)
- Eval pipeline with golden datasets
- Alerting and canary rollout
