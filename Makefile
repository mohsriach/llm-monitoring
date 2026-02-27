.PHONY: install run test lint compose-up

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
