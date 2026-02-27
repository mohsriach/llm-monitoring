.PHONY: install run test lint compose-up drift-check

install:
	pip install -e .[dev]

run:
	uvicorn serving.app:app --host 0.0.0.0 --port 8080 --reload

test:
	pytest -q

lint:
	ruff check src tests

compose-up:
	docker compose up --build

drift-check:
	PYTHONPATH=src python scripts/run_drift_check.py
