BACKEND_DIR := backend
IMAGE_NAME := fitcoach-api:local
COMPOSE := docker compose
PORT ?= 8000

.PHONY: help install run test lint format check qdrant-up qdrant-down qdrant-logs docker-build docker-run hooks pre-commit

help:
	@echo "make install       Sync Python dependencies"
	@echo "make run           Run FastAPI with reload"
	@echo "make test          Run tests"
	@echo "make lint          Run Ruff lint"
	@echo "make format        Format code with Ruff"
	@echo "make check         Run lint and tests"
	@echo "make qdrant-up     Start local Qdrant"
	@echo "make qdrant-down   Stop local Qdrant"
	@echo "make qdrant-logs   Follow Qdrant logs"
	@echo "make docker-build  Build FastAPI Docker image"
	@echo "make docker-run    Run FastAPI from Docker image"
	@echo "make hooks         Install Git pre-commit hook"
	@echo "make pre-commit    Run hooks for all files"

install:
	cd $(BACKEND_DIR) && uv sync

run:
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

test:
	cd $(BACKEND_DIR) && uv run python -m pytest $(TEST) $(PYTEST_ARGS)

lint:
	cd $(BACKEND_DIR) && uv run ruff check .

format:
	cd $(BACKEND_DIR) && uv run ruff format .

check: lint test

qdrant-up:
	$(COMPOSE) up -d qdrant

qdrant-down:
	$(COMPOSE) down

qdrant-logs:
	$(COMPOSE) logs -f qdrant

docker-build:
	docker build -t $(IMAGE_NAME) $(BACKEND_DIR)

docker-run:
	docker run --rm --env-file .env -p $(PORT):8000 $(IMAGE_NAME)

hooks:
	uv run --project $(BACKEND_DIR) pre-commit install

pre-commit:
	uv run --project $(BACKEND_DIR) pre-commit run --all-files