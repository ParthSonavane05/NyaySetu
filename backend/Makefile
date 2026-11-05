.PHONY: help install dev up down logs test lint format migrate shell

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

dev: ## Install dev dependencies
	pip install -e ".[dev]"
	pre-commit install

up: ## Start all services
	docker compose up -d --build

down: ## Stop all services
	docker compose down

logs: ## Tail API logs
	docker compose logs -f api

test: ## Run tests
	pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage
	pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

lint: ## Run linters
	ruff check app/ tests/
	mypy app/

format: ## Auto-format code
	ruff format app/ tests/
	ruff check --fix app/ tests/

migrate: ## Run Alembic migrations
	alembic upgrade head

migrate-new: ## Create a new migration (usage: make migrate-new MSG="add users")
	alembic revision --autogenerate -m "$(MSG)"

shell: ## Open a Python shell with app context
	python -c "import app; import code; code.interact(local=locals())"
