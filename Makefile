.PHONY: help docker-rebuild docker-down docker-up docker-prune migrate \
        test test-backend test-frontend test-e2e test-all test-coverage \
        lint lint-backend lint-frontend lint-all format-backend \
        backend-shell frontend-shell logs clean

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Docker & Database:"
	@echo "  make docker-rebuild       - Complete rebuild (stop, prune, rebuild, migrate)"
	@echo "  make docker-down          - Stop and remove all containers and volumes"
	@echo "  make docker-up            - Start containers in detached mode"
	@echo "  make docker-prune         - Remove all unused Docker resources"
	@echo "  make migrate              - Run database migrations (Alembic)"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 - Run all tests (backend + frontend)"
	@echo "  make test-backend         - Run backend tests with pytest"
	@echo "  make test-frontend        - Run frontend unit tests"
	@echo "  make test-e2e             - Run frontend E2E tests with Playwright"
	@echo "  make test-coverage        - Run tests with coverage report"
	@echo ""
	@echo "Linting & Formatting:"
	@echo "  make lint                 - Run all linters (backend + frontend)"
	@echo "  make lint-backend         - Run backend linters (ruff + mypy)"
	@echo "  make lint-frontend        - Run frontend ESLint"
	@echo "  make format-backend       - Format backend code with ruff"
	@echo ""
	@echo "Utilities:"
	@echo "  make backend-shell        - Open shell in backend container"
	@echo "  make frontend-shell       - Open shell in frontend container"
	@echo "  make logs                 - Show logs from all containers"
	@echo "  make clean                - Clean up temporary files and caches"

# ============================================================================
# Docker & Database Commands
# ============================================================================

docker-rebuild:
	@echo "🔨 Starting complete Docker rebuild..."
	@echo "⬇️  Stopping containers and removing volumes..."
	docker compose down -v
	@echo "🗑️  Pruning Docker system..."
	docker system prune -a -f
	@echo "🏗️  Building and starting containers..."
	docker compose up --build -d
	@echo "⏳ Waiting for services to initialize (migrations run automatically)..."
	@sleep 10
	@echo "✅ Docker rebuild complete!"
	@echo "📝 Check logs with: make logs"

docker-down:
	@echo "⬇️  Stopping containers and removing volumes..."
	docker compose down -v

docker-up:
	@echo "🚀 Starting containers..."
	docker compose up -d

docker-prune:
	@echo "🗑️  Pruning Docker system..."
	docker system prune -a -f

migrate:
	@echo "🗄️  Running database migrations..."
	docker compose exec backend alembic upgrade head

# ============================================================================
# Testing Commands
# ============================================================================

test: test-backend test-frontend
	@echo "✅ All tests completed!"

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && poetry run pytest

test-frontend:
	@echo "🧪 Running frontend unit tests..."
	cd frontend && npm run test:ci

test-e2e:
	@echo "🎭 Running E2E tests with Playwright..."
	cd frontend && npm run test:e2e

test-all: test-backend test-frontend test-e2e
	@echo "✅ All tests (unit + E2E) completed!"

test-coverage:
	@echo "📊 Running tests with coverage..."
	@echo "Backend coverage:"
	cd backend && poetry run pytest --cov --cov-report=term-missing
	@echo ""
	@echo "Frontend coverage:"
	cd frontend && npm run test:coverage

# ============================================================================
# Linting & Formatting Commands
# ============================================================================

lint: lint-backend lint-frontend
	@echo "✅ All linting completed!"

lint-backend:
	@echo "🔍 Running backend linters..."
	@echo "Running ruff..."
	cd backend && poetry run ruff check .
	@echo "Running mypy..."
	cd backend && poetry run mypy .

lint-frontend:
	@echo "🔍 Running frontend ESLint..."
	cd frontend && npm run lint

lint-all: lint-backend lint-frontend
	@echo "✅ All linting completed!"

format-backend:
	@echo "✨ Formatting backend code..."
	cd backend && poetry run ruff format .
	cd backend && poetry run ruff check --fix .

# ============================================================================
# Utility Commands
# ============================================================================

backend-shell:
	@echo "🐚 Opening backend container shell..."
	docker compose exec backend /bin/bash

frontend-shell:
	@echo "🐚 Opening frontend container shell..."
	docker compose exec frontend /bin/sh

logs:
	@echo "📋 Showing container logs..."
	docker compose logs -f

clean:
	@echo "🧹 Cleaning up temporary files and caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules/.cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"
