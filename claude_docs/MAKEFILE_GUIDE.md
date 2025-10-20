# Makefile Guide - Market Research Backend

## 📋 Overview

The Makefile provides convenient commands for common development tasks including testing, linting, type checking, formatting, Docker operations, and more.

**Quick Start**: Run `make help` to see all available commands.

---

## 🚀 Quick Reference

### Most Common Commands

```bash
make install        # Install dependencies
make dev            # Start development server
make test           # Run tests
make test-cov       # Run tests with coverage
make format         # Format code (black + isort)
make lint           # Run linters (flake8 + pylint)
make type-check     # Run mypy type checking
make quality        # Run format + lint + type-check
make docker-build   # Build Docker image
make docker-run     # Run Docker container
make clean          # Clean up generated files
```

---

## 📚 Command Categories

### Setup & Installation

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies with Poetry |
| `make install-dev` | Install including dev dependencies |
| `make update` | Update all dependencies |
| `make lock` | Generate poetry.lock file |

**Example**:
```bash
# First time setup
make install

# Update dependencies
make update
```

---

### Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-cov` | Run tests with HTML coverage report |
| `make test-cov-xml` | Run tests with XML coverage (for CI) |
| `make test-watch` | Run tests in watch mode |
| `make test-failed` | Re-run only failed tests |
| `make test-verbose` | Run tests with verbose output |
| `make test-unit` | Run only unit tests |
| `make test-integration` | Run only integration tests |

**Examples**:
```bash
# Basic testing
make test

# With coverage report
make test-cov
# Opens htmlcov/index.html

# Watch mode (re-runs on file changes)
make test-watch

# Run only failed tests
make test-failed
```

---

### Code Quality

| Command | Description |
|---------|-------------|
| `make format` | Format code with black and isort |
| `make format-check` | Check formatting without changes |
| `make lint` | Run all linters (flake8 + pylint) |
| `make lint-flake8` | Run flake8 only |
| `make lint-pylint` | Run pylint only |
| `make type-check` | Run mypy type checking |
| `make type-check-report` | Generate detailed type check report |
| `make quality` | Run format + lint + type-check |
| `make check` | Run all checks (format + lint + type + test) |

**Examples**:
```bash
# Format your code
make format

# Run all quality checks
make quality

# Full CI-style check
make check
```

**Quality Workflow**:
```bash
# 1. Format code
make format

# 2. Run linters
make lint

# 3. Type check
make type-check

# 4. Run tests
make test

# Or all in one:
make check
```

---

### Development

| Command | Description |
|---------|-------------|
| `make dev` | Start development server with auto-reload |
| `make dev-debug` | Start server with debug logging |
| `make shell` | Open Poetry shell |
| `make python` | Open Python REPL |

**Examples**:
```bash
# Start development server
make dev
# Server runs at http://localhost:8000
# Auto-reloads on code changes

# Debug mode
make dev-debug

# Interactive Python with app context
make python
>>> from app.models import survey
>>> from app.core import database
```

---

### Database

| Command | Description |
|---------|-------------|
| `make migrate` | Run database migrations |
| `make migrate-create MESSAGE="description"` | Create new migration |
| `make migrate-down` | Rollback last migration |
| `make migrate-history` | Show migration history |
| `make migrate-current` | Show current migration |

**Examples**:
```bash
# Run migrations
make migrate

# Create new migration
make migrate-create MESSAGE="add user avatar field"

# Rollback
make migrate-down

# Check status
make migrate-current
```

---

### Docker

| Command | Description |
|---------|-------------|
| `make docker-build` | Build Docker image |
| `make docker-build-no-cache` | Build without cache |
| `make docker-run` | Run container |
| `make docker-run-dev` | Run with volume mount |
| `make docker-stop` | Stop container |
| `make docker-remove` | Remove container |
| `make docker-restart` | Restart container |
| `make docker-logs` | Show container logs |
| `make docker-exec` | Execute bash in container |
| `make docker-clean` | Stop and remove container |
| `make docker-clean-all` | Remove container and image |
| `make docker-prune` | Remove all unused Docker resources |

**Examples**:
```bash
# Build and run
make docker-build
make docker-run

# View logs
make docker-logs

# Execute commands in container
make docker-exec
# Now you're in the container

# Rebuild from scratch
make docker-build-no-cache

# Full cleanup
make docker-clean-all
```

**Docker Compose** (alternative):
```bash
# Start all services (backend + db)
docker-compose up -d

# With pgAdmin
docker-compose --profile tools up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
```

---

### Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Clean generated files and caches |
| `make clean-all` | Clean everything including Docker |

**Examples**:
```bash
# Clean Python caches
make clean

# Clean everything
make clean-all
```

**What gets cleaned**:
- `__pycache__` directories
- `*.pyc`, `*.pyo` files
- `.pytest_cache`
- `.mypy_cache`
- `htmlcov/` (coverage reports)
- `.coverage` files
- `*.egg-info` directories

---

### Utilities

| Command | Description |
|---------|-------------|
| `make env-example` | Create .env.example from .env |
| `make show-env` | Show environment information |
| `make deps-outdated` | Show outdated dependencies |
| `make deps-tree` | Show dependency tree |
| `make info` | Show project information |

**Examples**:
```bash
# Check environment
make show-env

# Check for updates
make deps-outdated

# See dependency tree
make deps-tree
```

---

### All-in-One Commands

| Command | Description |
|---------|-------------|
| `make all` | Install + quality + test |
| `make ci` | Run all CI checks |
| `make pre-commit` | Format + lint + type-check + test-cov |
| `make build` | Clean + docker-build |
| `make deploy-prep` | Quality + test + docker-build |

**Examples**:
```bash
# Complete setup
make all

# Before committing
make pre-commit

# Prepare for deployment
make deploy-prep
```

---

## 🔄 Common Workflows

### Daily Development Workflow

```bash
# 1. Start development server
make dev

# 2. Make code changes...

# 3. Run tests
make test

# 4. Format and check quality
make quality

# 5. Commit changes
git add .
git commit -m "Your changes"
```

### Before Committing

```bash
# Run all pre-commit checks
make pre-commit

# This runs:
# - black (formatting)
# - isort (import sorting)
# - flake8 (linting)
# - pylint (linting)
# - mypy (type checking)
# - pytest with coverage
```

### CI/CD Pipeline

```bash
# What CI should run
make check

# This runs:
# - format-check (no changes, just verify)
# - lint (flake8 + pylint)
# - type-check (mypy)
# - test (all tests)
```

### Docker Development

```bash
# Build image
make docker-build

# Run container
make docker-run

# View logs
make docker-logs

# Stop and clean up
make docker-clean
```

### Adding New Feature

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes...

# 3. Run tests
make test-cov

# 4. Check quality
make quality

# 5. Format code
make format

# 6. Final check
make check

# 7. Commit
git add .
git commit -m "Add new feature"

# 8. Build Docker image
make docker-build
```

---

## 🎯 Best Practices

### Before Pushing Code

```bash
make pre-commit
```

This ensures:
- ✅ Code is formatted
- ✅ No linting errors
- ✅ No type errors
- ✅ All tests pass
- ✅ Good test coverage

### Setting Up New Developer

```bash
# 1. Clone repo
git clone <repo-url>
cd backend

# 2. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 3. Install dependencies
make install

# 4. Copy environment file
cp .env.example .env
# Edit .env with your settings

# 5. Run migrations
make migrate

# 6. Run tests
make test

# 7. Start development
make dev
```

### Deployment Checklist

```bash
# 1. Run all checks
make check

# 2. Build Docker image
make docker-build

# 3. Test Docker image locally
make docker-run
# Test API endpoints

# 4. Tag image
docker tag market-research-backend:latest registry.com/project:v1.0.0

# 5. Push image
docker push registry.com/project:v1.0.0
```

---

## 🐛 Troubleshooting

### "make: command not found"

**Solution**: Install make
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install
```

### "poetry: command not found"

**Solution**: Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Tests failing

```bash
# Run specific test to debug
poetry run pytest tests/test_specific.py -v

# Run with debugger
poetry run pytest tests/test_specific.py --pdb

# Show print statements
poetry run pytest tests/test_specific.py -s
```

### Docker build fails

```bash
# Clean and rebuild
make docker-clean-all
make docker-build-no-cache

# Check logs
make docker-logs
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
poetry run uvicorn app.main:app --port 8001
```

---

## 📊 Coverage Reports

After running `make test-cov`, open the coverage report:

```bash
# Open in browser (macOS)
open htmlcov/index.html

# Open in browser (Linux)
xdg-open htmlcov/index.html

# Or manually navigate to:
# backend/htmlcov/index.html
```

---

## 🔧 Customization

### Adding New Commands

Edit `Makefile` and add:

```makefile
my-command: ## Description of command
	@echo "Running my command..."
	# Your commands here
```

### Modifying Existing Commands

Find the command in `Makefile` and edit:

```makefile
test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	$(PYTEST) $(TESTS_DIR)/ -v --tb=short
```

---

## 📚 Related Documentation

- **Makefile** - The actual Makefile
- **POETRY_SETUP.md** - Poetry installation and usage
- **RESTRUCTURE_COMPLETE.md** - Backend structure
- **TESTING_SUMMARY.md** - Testing overview
- **Dockerfile** - Docker configuration
- **docker-compose.yml** - Docker Compose setup

---

## ✨ Summary

**The Makefile provides 50+ commands organized into 8 categories:**

1. **Setup**: install, update, lock
2. **Testing**: test, test-cov, test-watch
3. **Quality**: format, lint, type-check
4. **Development**: dev, shell, python
5. **Database**: migrate, migrate-create
6. **Docker**: docker-build, docker-run, docker-logs
7. **Cleanup**: clean, clean-all
8. **Utilities**: show-env, deps-tree, info

**Most used**:
- `make help` - See all commands
- `make install` - Setup project
- `make dev` - Start development
- `make test` - Run tests
- `make quality` - Check code quality
- `make docker-build` - Build Docker image

**For help**: Run `make help` or `make info`

---

**Last Updated**: 2025-10-20
**Author**: Claude Code
