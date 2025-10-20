# Poetry Setup Guide

Complete guide for using Poetry as the dependency manager for the Market Research Backend.

## 📚 Table of Contents

- [Why Poetry?](#why-poetry)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Common Commands](#common-commands)
- [Dependency Management](#dependency-management)
- [Virtual Environments](#virtual-environments)
- [Running Tests](#running-tests)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Migration from pip](#migration-from-pip)

---

## 🎯 Why Poetry?

Poetry provides several advantages over pip + requirements.txt:

### Benefits

✅ **Dependency Resolution**: Automatically resolves and locks dependencies
✅ **Lock File**: `poetry.lock` ensures reproducible builds
✅ **Virtual Environment Management**: Built-in venv handling
✅ **Dependency Groups**: Separate dev, test, and prod dependencies
✅ **Version Management**: Easy version bumping
✅ **Build System**: Standardized build backend
✅ **Scripts**: Define custom commands in `pyproject.toml`

### Comparison

| Feature | pip | Poetry |
|---------|-----|--------|
| Dependency Resolution | Manual | Automatic |
| Lock File | ❌ | ✅ `poetry.lock` |
| Dev Dependencies | Mixed in requirements.txt | Separate groups |
| Virtual Env | Manual venv | Built-in |
| Version Bumping | Manual | `poetry version` |
| Build System | setup.py | pyproject.toml |

---

## 📦 Installation

### Install Poetry

#### Linux / macOS / WSL

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### Windows (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

#### Alternative (via pipx - recommended)

```bash
# Install pipx if not installed
pip install pipx
pipx ensurepath

# Install Poetry via pipx
pipx install poetry
```

### Verify Installation

```bash
poetry --version
# Output: Poetry (version 1.7.0)
```

### Configure Poetry

```bash
# Use in-project virtual environments (recommended)
poetry config virtualenvs.in-project true

# View configuration
poetry config --list
```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
cd /home/mackers/tmg/marketResearch/backend
```

### 2. Install Dependencies

```bash
# Install all dependencies (production + dev)
poetry install

# Install only production dependencies
poetry install --only main

# Install without dev dependencies
poetry install --no-dev
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies
- Generate `poetry.lock` file

### 3. Activate Virtual Environment

```bash
# Activate the virtual environment
poetry shell

# Or run commands without activating
poetry run python script.py
```

### 4. Run Tests

```bash
# Using the test runner script
./run_tests.sh

# Or directly with Poetry
poetry run pytest

# With coverage
poetry run pytest --cov=. --cov-report=html
```

### 5. Run Application

```bash
# Development server
poetry run uvicorn main:app --reload

# Production
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🔧 Common Commands

### Dependency Management

```bash
# Add a production dependency
poetry add fastapi

# Add a specific version
poetry add fastapi@^0.104.0

# Add a dev dependency
poetry add --group dev pytest

# Add multiple dependencies
poetry add sqlalchemy alembic psycopg2-binary

# Remove a dependency
poetry remove package-name

# Update dependencies
poetry update

# Update a specific package
poetry update fastapi

# Show installed packages
poetry show

# Show dependency tree
poetry show --tree

# Show outdated packages
poetry show --outdated
```

### Virtual Environment

```bash
# Activate virtual environment
poetry shell

# Run command in virtual environment
poetry run python script.py
poetry run pytest
poetry run uvicorn main:app

# Show virtual environment info
poetry env info

# List virtual environments
poetry env list

# Remove virtual environment
poetry env remove python

# Create new virtual environment
poetry env use python3.11
```

### Project Management

```bash
# Initialize new project
poetry init

# Build package
poetry build

# Publish to PyPI (if applicable)
poetry publish

# Bump version
poetry version patch  # 1.0.0 -> 1.0.1
poetry version minor  # 1.0.0 -> 1.1.0
poetry version major  # 1.0.0 -> 2.0.0

# Export to requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt
poetry export --with dev -f requirements.txt --output requirements-dev.txt
```

### Testing & Quality

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=. --cov-report=html

# Run specific test file
poetry run pytest tests/test_json_utils.py

# Format code
poetry run black .

# Sort imports
poetry run isort .

# Type checking
poetry run mypy .

# Linting
poetry run pylint *.py

# Run all quality checks
poetry run black . && poetry run isort . && poetry run mypy . && poetry run pytest
```

---

## 📝 Dependency Management

### Understanding Dependency Groups

The `pyproject.toml` defines several dependency groups:

```toml
[tool.poetry.dependencies]
# Main/production dependencies
python = "^3.11"
fastapi = "^0.104.1"
...

[tool.poetry.group.dev.dependencies]
# Development dependencies (testing, linting, etc.)
pytest = "^7.4.0"
black = "^23.11.0"
...

[tool.poetry.group.docs.dependencies]
# Documentation dependencies (optional)
mkdocs = "^1.5.3"
...
```

### Version Constraints

Poetry uses semantic versioning constraints:

```toml
# Caret (^) - Compatible versions
fastapi = "^0.104.1"  # >=0.104.1, <0.105.0

# Tilde (~) - Patch updates
uvicorn = "~0.24.0"  # >=0.24.0, <0.25.0

# Wildcard (*) - Any version
requests = "*"

# Exact version
sqlalchemy = "==2.0.23"

# Multiple constraints
pydantic = ">=2.0.0, <3.0.0"
```

### Adding Dependencies

```bash
# Add to main dependencies
poetry add requests

# Add to dev dependencies
poetry add --group dev pytest-mock

# Add with extras
poetry add uvicorn[standard]
poetry add pydantic[email]

# Add from git repository
poetry add git+https://github.com/user/repo.git

# Add from local path
poetry add ../my-local-package
```

---

## 🔒 Virtual Environments

### Working with Virtual Environments

```bash
# Activate virtual environment
poetry shell
# Now you're in the virtualenv, prompt will change

# Deactivate (from inside virtualenv)
exit

# Run single command without activation
poetry run python -c "import fastapi; print(fastapi.__version__)"

# Check which Python is being used
poetry run which python

# Install dependencies without creating virtualenv
poetry install --no-dev
```

### Environment Information

```bash
# Show environment info
poetry env info

# Output:
# Virtualenv
# Python:         3.11.0
# Implementation: CPython
# Path:           /path/to/project/.venv
# Executable:     /path/to/project/.venv/bin/python
# Valid:          True
```

### Multiple Python Versions

```bash
# Use specific Python version
poetry env use python3.11
poetry env use /usr/bin/python3.10

# List available environments
poetry env list

# Remove an environment
poetry env remove 3.11
```

---

## 🧪 Running Tests

### Basic Testing

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_json_utils.py

# Run specific test
poetry run pytest tests/test_json_utils.py::TestSafeJsonParse::test_parse_valid_json_array
```

### Coverage

```bash
# Run tests with coverage
poetry run pytest --cov=.

# Generate HTML report
poetry run pytest --cov=. --cov-report=html

# Open coverage report
poetry run pytest --cov=. --cov-report=html && open htmlcov/index.html
```

### Using Test Runner Script

```bash
# Make executable (first time only)
chmod +x run_tests.sh

# Run all tests
./run_tests.sh

# Run with coverage
./run_tests.sh --coverage

# Run specific test
./run_tests.sh --test test_json_utils.py

# Verbose mode
./run_tests.sh --verbose
```

### Custom Test Scripts

Poetry allows defining custom scripts in `pyproject.toml`:

```toml
[tool.poetry.scripts]
test = "pytest"
test-cov = "pytest --cov=. --cov-report=html"
```

Usage:

```bash
poetry run test
poetry run test-cov
```

---

## 💻 Development Workflow

### Daily Development

```bash
# 1. Activate environment
poetry shell

# 2. Install/update dependencies
poetry install

# 3. Make code changes
# ... edit files ...

# 4. Run tests
poetry run pytest

# 5. Format code
poetry run black .
poetry run isort .

# 6. Run linting
poetry run mypy .
poetry run pylint *.py

# 7. Commit changes
git add .
git commit -m "Your changes"
```

### Adding New Features

```bash
# 1. Create new branch
git checkout -b feature/new-feature

# 2. Add new dependencies if needed
poetry add new-package

# 3. Develop feature
# ... write code ...

# 4. Write tests
# ... write tests ...

# 5. Run tests
poetry run pytest

# 6. Commit
git add .
git commit -m "Add new feature"

# 7. Update lock file
git add poetry.lock
git commit -m "Update dependencies"
```

### Code Quality Workflow

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Type check
poetry run mypy .

# Run tests
poetry run pytest

# Check coverage
poetry run pytest --cov=. --cov-report=term-missing

# All in one command
poetry run black . && \
poetry run isort . && \
poetry run mypy . && \
poetry run pytest --cov=.
```

---

## 🔍 Troubleshooting

### Common Issues

#### Issue: Poetry command not found

```bash
# Solution: Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Issue: Virtual environment not activating

```bash
# Solution: Recreate virtual environment
poetry env remove python
poetry install
```

#### Issue: Dependency conflicts

```bash
# Solution 1: Update lock file
poetry lock

# Solution 2: Clear cache and reinstall
poetry cache clear pypi --all
rm poetry.lock
poetry install
```

#### Issue: Wrong Python version

```bash
# Solution: Specify Python version
poetry env use python3.11
poetry install
```

#### Issue: Import errors in tests

```bash
# Solution: Ensure you're using Poetry's environment
poetry run pytest
# Or
poetry shell
pytest
```

#### Issue: Slow dependency resolution

```bash
# Solution: Update Poetry
poetry self update

# Or clear cache
poetry cache clear pypi --all
```

### Debug Commands

```bash
# Check Poetry configuration
poetry config --list

# Show environment info
poetry env info

# Check dependency tree
poetry show --tree

# Validate pyproject.toml
poetry check

# Show Poetry version
poetry --version

# Enable debug output
poetry -vvv install
```

---

## 🔄 Migration from pip

### If You Have requirements.txt

```bash
# 1. Initialize Poetry in existing project
poetry init

# 2. Add dependencies from requirements.txt
cat requirements.txt | grep -v "^#" | xargs poetry add

# 3. Add dev dependencies from requirements-test.txt
cat requirements-test.txt | grep -v "^#" | xargs poetry add --group dev

# 4. Lock dependencies
poetry lock

# 5. Install
poetry install

# 6. Test
poetry run pytest

# 7. Once verified, can remove old files
# rm requirements.txt requirements-test.txt
```

### Gradual Migration

You can use both systems temporarily:

```bash
# Keep using pip in CI while testing Poetry locally
poetry export -f requirements.txt --output requirements.txt

# This generates requirements.txt from poetry.lock
# Your CI can continue using pip install -r requirements.txt
```

---

## 📚 Additional Resources

### Official Documentation
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry Commands](https://python-poetry.org/docs/cli/)
- [Dependency Specification](https://python-poetry.org/docs/dependency-specification/)

### Best Practices
- [Poetry Best Practices](https://python-poetry.org/docs/best-practices/)
- [Managing Dependencies](https://python-poetry.org/docs/managing-dependencies/)

### Related Docs
- `REFACTORING_SUMMARY.md` - Backend refactoring overview
- `QUICK_REFERENCE.md` - Quick reference for utilities
- `TESTING_SUMMARY.md` - Testing documentation
- `tests/README.md` - Detailed testing guide

---

## 🎯 Quick Command Reference

| Task | Command |
|------|---------|
| Install dependencies | `poetry install` |
| Add package | `poetry add package-name` |
| Add dev package | `poetry add --group dev package-name` |
| Remove package | `poetry remove package-name` |
| Update dependencies | `poetry update` |
| Activate shell | `poetry shell` |
| Run command | `poetry run command` |
| Run tests | `poetry run pytest` |
| Run tests with coverage | `poetry run pytest --cov=.` |
| Format code | `poetry run black .` |
| Type check | `poetry run mypy .` |
| Export requirements | `poetry export -f requirements.txt -o requirements.txt` |
| Show environment | `poetry env info` |
| Remove environment | `poetry env remove python` |

---

## ✅ Checklist for New Developers

- [ ] Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- [ ] Configure Poetry: `poetry config virtualenvs.in-project true`
- [ ] Clone repository
- [ ] Install dependencies: `poetry install`
- [ ] Activate environment: `poetry shell`
- [ ] Run tests: `poetry run pytest`
- [ ] Verify setup: `poetry env info`
- [ ] Read documentation: `REFACTORING_SUMMARY.md`

---

**Last Updated**: 2025-10-20
**Poetry Version**: 1.7.0+
**Python Version**: 3.11+
