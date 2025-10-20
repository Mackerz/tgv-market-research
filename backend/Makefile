.PHONY: help install test test-cov test-watch lint format type-check quality check docker-build docker-run docker-stop docker-clean dev migrate clean all

# Variables
POETRY := poetry
PYTHON := $(POETRY) run python
PYTEST := $(POETRY) run pytest
BLACK := $(POETRY) run black
ISORT := $(POETRY) run isort
MYPY := $(POETRY) run mypy
FLAKE8 := $(POETRY) run flake8
PYLINT := $(POETRY) run pylint
UVICORN := $(POETRY) run uvicorn

# Docker variables
DOCKER_IMAGE := market-research-backend
DOCKER_TAG := latest
DOCKER_CONTAINER := market-research-backend-container

# Directories
APP_DIR := app
TESTS_DIR := tests
SCRIPTS_DIR := scripts

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Help

help: ## Display this help message
	@echo "$(GREEN)Market Research Backend - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

install: ## Install all dependencies with Poetry
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(POETRY) install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-dev: ## Install dependencies including dev tools
	@echo "$(GREEN)Installing all dependencies (including dev)...$(NC)"
	$(POETRY) install --with dev
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

update: ## Update dependencies
	@echo "$(YELLOW)Updating dependencies...$(NC)"
	$(POETRY) update
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

lock: ## Generate poetry.lock file
	@echo "$(YELLOW)Generating lock file...$(NC)"
	$(POETRY) lock
	@echo "$(GREEN)✓ Lock file generated$(NC)"

##@ Testing

test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	$(PYTEST) $(TESTS_DIR)/

test-cov: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	$(PYTEST) --cov=$(APP_DIR) --cov-report=html --cov-report=term-missing $(TESTS_DIR)/
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/index.html$(NC)"

test-cov-xml: ## Run tests with XML coverage (for CI)
	@echo "$(GREEN)Running tests with XML coverage...$(NC)"
	$(PYTEST) --cov=$(APP_DIR) --cov-report=xml --cov-report=term $(TESTS_DIR)/

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	$(PYTEST) -f $(TESTS_DIR)/

test-failed: ## Run only failed tests
	@echo "$(YELLOW)Running failed tests...$(NC)"
	$(PYTEST) --lf $(TESTS_DIR)/

test-verbose: ## Run tests with verbose output
	@echo "$(GREEN)Running tests (verbose)...$(NC)"
	$(PYTEST) -vv $(TESTS_DIR)/

test-unit: ## Run only unit tests
	@echo "$(GREEN)Running unit tests...$(NC)"
	$(PYTEST) -m unit $(TESTS_DIR)/

test-integration: ## Run only integration tests
	@echo "$(GREEN)Running integration tests...$(NC)"
	$(PYTEST) -m integration $(TESTS_DIR)/

##@ Code Quality

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	$(BLACK) $(APP_DIR) $(TESTS_DIR) $(SCRIPTS_DIR)
	$(ISORT) $(APP_DIR) $(TESTS_DIR) $(SCRIPTS_DIR)
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check if code is formatted correctly (no changes)
	@echo "$(YELLOW)Checking code formatting...$(NC)"
	$(BLACK) --check $(APP_DIR) $(TESTS_DIR) $(SCRIPTS_DIR)
	$(ISORT) --check-only $(APP_DIR) $(TESTS_DIR) $(SCRIPTS_DIR)
	@echo "$(GREEN)✓ Code formatting is correct$(NC)"

lint: ## Run all linters (flake8, pylint)
	@echo "$(GREEN)Running linters...$(NC)"
	@echo "$(YELLOW)→ Running flake8...$(NC)"
	-$(FLAKE8) $(APP_DIR) $(TESTS_DIR)
	@echo "$(YELLOW)→ Running pylint...$(NC)"
	-$(PYLINT) $(APP_DIR)/**/*.py
	@echo "$(GREEN)✓ Linting complete$(NC)"

lint-flake8: ## Run flake8 only
	@echo "$(GREEN)Running flake8...$(NC)"
	$(FLAKE8) $(APP_DIR) $(TESTS_DIR)

lint-pylint: ## Run pylint only
	@echo "$(GREEN)Running pylint...$(NC)"
	$(PYLINT) $(APP_DIR)/**/*.py

type-check: ## Run mypy type checking
	@echo "$(GREEN)Running type checks...$(NC)"
	$(MYPY) $(APP_DIR)
	@echo "$(GREEN)✓ Type checking complete$(NC)"

type-check-report: ## Run mypy with detailed report
	@echo "$(GREEN)Running type checks (detailed)...$(NC)"
	$(MYPY) $(APP_DIR) --html-report mypy-report
	@echo "$(GREEN)✓ Type check report generated in mypy-report/index.html$(NC)"

quality: format lint type-check ## Run all quality checks (format, lint, type-check)
	@echo "$(GREEN)✓ All quality checks passed$(NC)"

check: format-check lint type-check test ## Run all checks (format, lint, type, test) - CI ready
	@echo "$(GREEN)✓ All checks passed$(NC)"

##@ Development

dev: ## Run development server with auto-reload
	@echo "$(GREEN)Starting development server...$(NC)"
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

dev-debug: ## Run development server with debug logging
	@echo "$(GREEN)Starting development server (debug mode)...$(NC)"
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

shell: ## Open Poetry shell
	@echo "$(GREEN)Opening Poetry shell...$(NC)"
	$(POETRY) shell

python: ## Open Python REPL in Poetry environment
	@echo "$(GREEN)Opening Python REPL...$(NC)"
	$(PYTHON)

##@ Database

migrate: ## Run database migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	$(PYTHON) -m alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

migrate-create: ## Create a new migration (use MESSAGE="description")
	@echo "$(GREEN)Creating migration...$(NC)"
	$(PYTHON) -m alembic revision --autogenerate -m "$(MESSAGE)"
	@echo "$(GREEN)✓ Migration created$(NC)"

migrate-down: ## Rollback last migration
	@echo "$(YELLOW)Rolling back migration...$(NC)"
	$(PYTHON) -m alembic downgrade -1
	@echo "$(GREEN)✓ Migration rolled back$(NC)"

migrate-history: ## Show migration history
	@echo "$(GREEN)Migration history:$(NC)"
	$(PYTHON) -m alembic history

migrate-current: ## Show current migration
	@echo "$(GREEN)Current migration:$(NC)"
	$(PYTHON) -m alembic current

##@ Docker

docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✓ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

docker-build-no-cache: ## Build Docker image without cache
	@echo "$(GREEN)Building Docker image (no cache)...$(NC)"
	docker build --no-cache -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(GREEN)Starting Docker container...$(NC)"
	docker run -d \
		--name $(DOCKER_CONTAINER) \
		-p 8000:8000 \
		--env-file .env \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)✓ Container started: $(DOCKER_CONTAINER)$(NC)"
	@echo "$(YELLOW)→ API available at http://localhost:8000$(NC)"

docker-run-dev: ## Run Docker container with volume mount for development
	@echo "$(GREEN)Starting Docker container (development mode)...$(NC)"
	docker run -d \
		--name $(DOCKER_CONTAINER) \
		-p 8000:8000 \
		-v $(PWD):/app \
		--env-file .env \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)✓ Container started with volume mount$(NC)"

docker-stop: ## Stop Docker container
	@echo "$(YELLOW)Stopping Docker container...$(NC)"
	docker stop $(DOCKER_CONTAINER) || true
	@echo "$(GREEN)✓ Container stopped$(NC)"

docker-remove: ## Remove Docker container
	@echo "$(YELLOW)Removing Docker container...$(NC)"
	docker rm $(DOCKER_CONTAINER) || true
	@echo "$(GREEN)✓ Container removed$(NC)"

docker-restart: docker-stop docker-remove docker-run ## Restart Docker container

docker-logs: ## Show Docker container logs
	@echo "$(GREEN)Showing container logs...$(NC)"
	docker logs -f $(DOCKER_CONTAINER)

docker-exec: ## Execute bash in running container
	@echo "$(GREEN)Connecting to container...$(NC)"
	docker exec -it $(DOCKER_CONTAINER) /bin/bash

docker-clean: docker-stop docker-remove ## Stop and remove container
	@echo "$(GREEN)✓ Docker cleanup complete$(NC)"

docker-clean-all: docker-clean ## Remove container and image
	@echo "$(YELLOW)Removing Docker image...$(NC)"
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) || true
	@echo "$(GREEN)✓ Docker cleanup complete$(NC)"

docker-prune: ## Remove all unused Docker resources
	@echo "$(YELLOW)Pruning Docker resources...$(NC)"
	docker system prune -af
	@echo "$(GREEN)✓ Docker prune complete$(NC)"

##@ Cleanup

clean: ## Clean up generated files and caches
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean docker-clean-all ## Clean everything including Docker

##@ Utilities

env-example: ## Create .env.example from current .env
	@echo "$(YELLOW)Creating .env.example...$(NC)"
	@if [ -f .env ]; then \
		grep -v -E "^(.*=.*[^=]$$)" .env > .env.example || true; \
		sed 's/=.*/=/' .env > .env.example; \
		echo "$(GREEN)✓ .env.example created$(NC)"; \
	else \
		echo "$(RED)✗ .env file not found$(NC)"; \
	fi

show-env: ## Show environment information
	@echo "$(GREEN)Environment Information:$(NC)"
	@echo "Poetry version: $$($(POETRY) --version)"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Working directory: $$(pwd)"
	@echo "Docker available: $$(docker --version 2>/dev/null || echo 'Not installed')"

deps-outdated: ## Show outdated dependencies
	@echo "$(YELLOW)Checking for outdated dependencies...$(NC)"
	$(POETRY) show --outdated

deps-tree: ## Show dependency tree
	@echo "$(GREEN)Dependency tree:$(NC)"
	$(POETRY) show --tree

##@ All-in-One Commands

all: install quality test ## Install, check quality, and run tests
	@echo "$(GREEN)✓ All tasks complete$(NC)"

ci: check ## Run all CI checks (same as 'check')
	@echo "$(GREEN)✓ CI checks passed$(NC)"

pre-commit: format lint type-check test-cov ## Run pre-commit checks
	@echo "$(GREEN)✓ Pre-commit checks passed$(NC)"

build: clean docker-build ## Clean and build Docker image
	@echo "$(GREEN)✓ Build complete$(NC)"

deploy-prep: quality test docker-build ## Prepare for deployment
	@echo "$(GREEN)✓ Ready for deployment$(NC)"

##@ Information

info: ## Show project information
	@echo "$(GREEN)================================$(NC)"
	@echo "$(GREEN)Market Research Backend$(NC)"
	@echo "$(GREEN)================================$(NC)"
	@echo ""
	@echo "Project Structure:"
	@echo "  - $(APP_DIR)/          Application code"
	@echo "  - $(TESTS_DIR)/        Test files"
	@echo "  - $(SCRIPTS_DIR)/      Utility scripts"
	@echo ""
	@echo "Key Commands:"
	@echo "  - make install       Install dependencies"
	@echo "  - make dev           Start development server"
	@echo "  - make test          Run tests"
	@echo "  - make quality       Run all quality checks"
	@echo "  - make docker-build  Build Docker image"
	@echo ""
	@echo "Run 'make help' for all available commands"

.DEFAULT_GOAL := help
