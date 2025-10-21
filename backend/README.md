# Market Research Backend

A modern FastAPI-based backend service for market research surveys with AI-powered media analysis, built with Python 3.11, SQLAlchemy, and Google Cloud services.

## Features

- 🚀 **FastAPI** - High-performance async web framework
- 🗄️ **SQLAlchemy** - Robust ORM with PostgreSQL
- 🔐 **Security** - API key authentication, rate limiting, CSRF protection, input validation
- 🤖 **AI Analysis** - Google Cloud Vision & Video Intelligence integration
- 📊 **Survey Management** - Dynamic survey flow with multiple question types
- 🎨 **Media Processing** - Photo and video upload with validation and AI analysis
- 📈 **Performance** - Optimized queries, connection pooling, eager loading
- ✅ **Type Safe** - MyPy type checking throughout
- 🧪 **Well Tested** - Comprehensive test suite with 59+ unit tests

## Tech Stack

### Core
- **Python 3.11**
- **FastAPI 0.104.1** - Web framework
- **SQLAlchemy 2.0.23** - ORM
- **PostgreSQL** - Database
- **Alembic** - Database migrations
- **Pydantic 2.5.0** - Data validation

### Security & Validation
- **slowapi** - Rate limiting
- **python-jose** - JWT authentication
- **passlib** - Password hashing
- **bleach** - HTML sanitization
- **python-magic** - File type validation

### Google Cloud Services
- **Google Cloud Storage** - Media storage
- **Google Cloud Vision** - Image analysis
- **Google Cloud Video Intelligence** - Video analysis
- **Google Generative AI** - AI-powered insights
- **Google Cloud Secret Manager** - Secrets management

### Development Tools
- **Poetry** - Dependency management
- **Ruff** - Linting and formatting (10-100x faster than black/flake8/pylint)
- **MyPy** - Static type checking
- **Pytest** - Testing framework with async support

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Poetry (installed automatically if not present)
- Google Cloud Platform account (for production features)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd backend

# Install dependencies with Poetry
make install-dev

# Or manually
poetry install --with dev
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required: DATABASE_URL, GCP credentials (for production)
```

### Database Setup

```bash
# Run migrations
make migrate

# Or manually
poetry run alembic upgrade head
```

### Development Server

```bash
# Start development server with auto-reload
make dev

# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Development Workflow

### Daily Commands

```bash
# Format code
make format

# Fix linting issues
make lint-fix

# Run type checking
make type-check

# Run tests
make test

# Run all quality checks
make quality
```

### Before Committing

```bash
# Run all pre-commit checks (format + lint + type-check + test coverage)
make pre-commit
```

### Working with Poetry

```bash
# Add a new dependency
poetry add <package-name>

# Add a dev dependency
poetry add --group dev <package-name>

# Update dependencies
make update

# Show installed packages
poetry show

# Show outdated packages
make deps-outdated
```

## Available Make Commands

### Setup & Installation
- `make install` - Install production dependencies
- `make install-dev` - Install all dependencies (including dev tools)
- `make update` - Update dependencies
- `make lock` - Generate poetry.lock file

### Testing
- `make test` - Run all tests
- `make test-cov` - Run tests with coverage report
- `make test-verbose` - Run tests with verbose output
- `make test-unit` - Run only unit tests
- `make test-integration` - Run only integration tests

### Code Quality
- `make format` - Format code with ruff
- `make format-check` - Check formatting (no changes)
- `make lint` - Run ruff linter
- `make lint-fix` - Auto-fix linting issues
- `make type-check` - Run mypy type checking
- `make quality` - Run all quality checks

### Development
- `make dev` - Start development server
- `make dev-debug` - Start server with debug logging
- `make shell` - Open Poetry shell
- `make show-env` - Show environment information

### Database
- `make migrate` - Run database migrations
- `make migrate-create MESSAGE="description"` - Create new migration
- `make migrate-down` - Rollback last migration
- `make migrate-history` - Show migration history

### Docker
- `make docker-build` - Build Docker image
- `make docker-run` - Run Docker container
- `make docker-clean` - Stop and remove container

### CI/CD
- `make ci` - Run all CI checks
- `make pre-commit` - Run pre-commit checks
- `make check` - Run all checks (CI ready)

### Utilities
- `make clean` - Clean up caches and generated files
- `make help` - Show all available commands

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/              # API endpoints
│   │       ├── router.py    # Main API router
│   │       ├── surveys.py   # Survey endpoints
│   │       ├── submissions.py  # Submission endpoints
│   │       ├── media.py     # Media upload endpoints
│   │       └── health.py    # Health check endpoints
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   ├── auth.py          # Authentication
│   │   ├── csrf.py          # CSRF protection
│   │   └── error_handlers.py  # Error handling
│   ├── crud/
│   │   └── survey.py        # Database operations
│   ├── models/
│   │   ├── survey.py        # Survey models
│   │   ├── media.py         # Media models
│   │   └── user.py          # User models
│   ├── schemas/
│   │   └── survey.py        # Pydantic schemas
│   ├── utils/
│   │   └── validation.py    # Input validation utilities
│   ├── integrations/
│   │   └── gcp/             # Google Cloud integrations
│   └── main.py              # Application entry point
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── test_validation.py  # Validation tests
│   ├── test_csrf.py        # CSRF protection tests
│   ├── test_auth_security.py  # Auth tests
│   └── test_n_plus_one_queries.py  # Performance tests
├── alembic/                 # Database migrations
├── pyproject.toml          # Project configuration
├── poetry.lock             # Locked dependencies
├── Makefile                # Development commands
└── README.md               # This file
```

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Security Features

### Implemented Security Measures

1. **Authentication**
   - API key-based authentication for admin endpoints
   - Fail-closed behavior in production
   - Constant-time comparison for timing attack prevention

2. **Rate Limiting**
   - Endpoint-specific rate limits
   - IP-based throttling
   - Protection against DoS attacks

3. **Input Validation**
   - File upload validation (size, type, magic bytes)
   - Email validation with disposable domain blocking
   - HTML sanitization for XSS prevention
   - SQL injection prevention via SQLAlchemy ORM

4. **CSRF Protection**
   - Token-based CSRF protection (opt-in)
   - Time-limited tokens
   - Secure token generation

5. **Security Headers**
   - CORS configuration
   - Content Security Policy
   - X-Frame-Options
   - X-Content-Type-Options

6. **Data Protection**
   - Secrets stored in Google Cloud Secret Manager
   - Environment-based configuration
   - No hardcoded credentials

## Performance Optimizations

- ✅ **N+1 Query Prevention** - Eager loading with selectinload
- ✅ **Connection Pooling** - PostgreSQL connection pooling
- ✅ **Database Indexes** - Optimized indexes on frequently queried columns
- ✅ **Async Operations** - FastAPI async endpoints
- ✅ **Response Caching** - Where appropriate

## Testing

### Run Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
poetry run pytest tests/test_validation.py -v

# Run specific test
poetry run pytest tests/test_validation.py::TestFileValidator::test_validate_image_valid_jpeg -v
```

### Test Coverage

Current test coverage includes:
- ✅ File upload validation (13 tests)
- ✅ Email validation (9 tests)
- ✅ Input sanitization (9 tests)
- ✅ CSRF protection (15 tests)
- ✅ Authentication security (9 tests)
- ✅ N+1 query optimization (4 tests)

**Total: 59+ comprehensive unit tests**

## Code Quality

### Linting & Formatting

We use **Ruff** - a modern, fast Python linter and formatter written in Rust:

```bash
# Format code
make format

# Check linting
make lint

# Auto-fix issues
make lint-fix
```

### Type Checking

We use **MyPy** for static type checking:

```bash
# Run type checking
make type-check

# Generate HTML report
make type-check-report
```

### Pre-commit Checks

Before committing, run:

```bash
make pre-commit
```

This runs:
1. Code formatting check
2. Linting
3. Type checking
4. Full test suite with coverage

## Environment Variables

### Required (Development)

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ENVIRONMENT=development
```

### Required (Production)

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ENVIRONMENT=production
API_KEY=<your-secure-api-key>
SECRET_KEY=<your-secret-key>

# Google Cloud
GCP_PROJECT_ID=<project-id>
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GCS_PHOTO_BUCKET=<bucket-name>
GCS_VIDEO_BUCKET=<bucket-name>
GEMINI_API_KEY=<api-key>
```

### Optional

```bash
# CSRF Protection (disabled by default)
CSRF_PROTECTION_ENABLED=true

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
```

## Deployment

### Using Docker

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

### Manual Deployment

```bash
# Install production dependencies only
poetry install --without dev

# Run with gunicorn (recommended for production)
poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Database Migrations

### Create Migration

```bash
# Auto-generate migration from model changes
make migrate-create MESSAGE="Add new field to survey"
```

### Apply Migrations

```bash
# Apply all pending migrations
make migrate
```

### Rollback

```bash
# Rollback last migration
make migrate-down
```

## Troubleshooting

### Poetry not found

```bash
# Add Poetry to PATH
export PATH="/home/mackers/.local/bin:$PATH"

# Or install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

### Database connection errors

1. Ensure PostgreSQL is running
2. Check DATABASE_URL in .env
3. Verify database exists
4. Check network connectivity

### Import errors

```bash
# Reinstall dependencies
make clean
make install-dev
```

### Test failures

```bash
# Run tests with verbose output
make test-verbose

# Run specific failing test
poetry run pytest tests/test_name.py::test_function -vv
```

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install dependencies (`make install-dev`)
4. Make your changes
5. Run tests (`make test`)
6. Run quality checks (`make quality`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide (enforced by Ruff)
- Add type hints (checked by MyPy)
- Write tests for new features
- Update documentation as needed
- Run `make pre-commit` before pushing

## Documentation

- **API Docs**: http://localhost:8000/docs (when server is running)
- **Migration Summary**: See `POETRY_MIGRATION_SUMMARY.md`
- **Quick Reference**: See `QUICK_REFERENCE.md`
- **Code Reviews**: See `COMPREHENSIVE_CODE_REVIEW_2025.md`

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team

## Changelog

### Recent Updates (October 2025)

- ✅ Migrated to Poetry for dependency management
- ✅ Replaced black/isort/flake8/pylint with Ruff (10-100x faster)
- ✅ Added comprehensive MyPy type checking
- ✅ Implemented security fixes (auth, CSRF, input validation)
- ✅ Optimized database queries (N+1 prevention, connection pooling)
- ✅ Added 59+ unit tests with 100% coverage of security features
- ✅ Enhanced Makefile with developer-friendly commands
- ✅ Updated all dependencies to latest stable versions

---

**Built with ❤️ using Python, FastAPI, and modern best practices**
