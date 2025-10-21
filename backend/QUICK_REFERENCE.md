# Quick Reference Guide - Poetry & Ruff

## Common Commands

### Development Workflow
```bash
# Start development server
make dev

# Format code
make format

# Fix linting issues
make lint-fix

# Check types
make type-check

# Run tests
make test

# Run all quality checks
make quality
```

### Before Committing
```bash
# Run all pre-commit checks (format + lint + type-check + test with coverage)
make pre-commit
```

### Installing Dependencies
```bash
# Install dependencies (production + dev)
make install-dev

# Install production dependencies only
make install

# Update all dependencies
make update
```

### Running Tests
```bash
# Run all tests
make test

# Run tests with coverage report
make test-cov

# Run specific test file
poetry run pytest tests/test_validation.py -v

# Run specific test
poetry run pytest tests/test_validation.py::TestFileValidator::test_validate_image_valid_jpeg -v
```

### Linting & Formatting

#### Ruff (replaces black, isort, flake8, pylint)
```bash
# Check formatting (no changes)
make format-check

# Format code
make format

# Check linting issues
make lint

# Fix linting issues automatically
make lint-fix

# Fix with unsafe fixes (be careful!)
make lint-unsafe-fix

# Check specific file
poetry run ruff check app/core/auth.py

# Format specific file
poetry run ruff format app/core/auth.py

# Show available rules
poetry run ruff rule --all
```

#### MyPy Type Checking
```bash
# Run type checking
make type-check

# Generate HTML report
make type-check-report

# Check specific file
poetry run mypy app/core/auth.py
```

### Poetry Commands
```bash
# Add a new dependency
poetry add <package-name>

# Add a dev dependency
poetry add --group dev <package-name>

# Remove a dependency
poetry remove <package-name>

# Show installed packages
poetry show

# Show outdated packages
make deps-outdated

# Show dependency tree
make deps-tree

# Update poetry.lock
make lock

# Open Poetry shell
make shell
```

### Database Migrations
```bash
# Run migrations
make migrate

# Create new migration
make migrate-create MESSAGE="description"

# Rollback last migration
make migrate-down

# Show migration history
make migrate-history
```

### Docker
```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run

# Stop and remove container
make docker-clean

# View logs
make docker-logs
```

### Utilities
```bash
# Show environment information
make show-env

# Clean up caches and generated files
make clean

# Show all available commands
make help
```

## CI/CD Integration

```bash
# Run all CI checks (format-check + lint + type-check + test)
make ci
```

## Configuration Files

- **`pyproject.toml`** - All project configuration (Poetry, Ruff, MyPy, Pytest, Coverage)
- **`poetry.lock`** - Locked dependencies (commit this!)
- **`Makefile`** - All make commands

## Ruff Configuration Highlights

### Enabled Features:
- ✅ Auto-formatting (like black)
- ✅ Import sorting (like isort)
- ✅ Linting (like flake8 + pylint + 20+ other tools)
- ✅ Security checks (bandit)
- ✅ Performance checks
- ✅ Bug detection
- ✅ Type annotation checks

### Key Settings:
- Line length: 100
- Target: Python 3.11
- Auto-fix available for most rules
- Tests have relaxed rules

## Troubleshooting

### Poetry not found
```bash
export PATH="/home/mackers/.local/bin:$PATH"
```

### Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Verify Installation
```bash
make show-env
```

### Update Dependencies After Branch Switch
```bash
make install-dev
```

### Clear Caches
```bash
make clean
```

## Pro Tips

1. **Use `make lint-fix`** - Automatically fixes most linting issues
2. **Use `make format`** - Formats all code consistently
3. **Run `make pre-commit`** before pushing - Catches issues early
4. **Use `make quality`** - Runs all quality checks at once
5. **Check `make help`** - Lists all available commands

## Example Workflow

```bash
# 1. Make changes to code
vim app/api/v1/surveys.py

# 2. Format and fix issues
make format
make lint-fix

# 3. Check types
make type-check

# 4. Run tests
make test

# 5. Before commit - run everything
make pre-commit

# 6. Commit changes
git add .
git commit -m "feat: add new survey endpoint"
```

## VSCode Integration (Optional)

Add to `.vscode/settings.json`:
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "python.linting.enabled": false,
  "ruff.enable": true,
  "ruff.lint.run": "onType"
}
```

Install Ruff extension: `charliermarsh.ruff`
