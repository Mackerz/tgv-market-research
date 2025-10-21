# Multi-stage Dockerfile for Market Research Backend

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies only (no dev dependencies for production)
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

# Stage 2: Runtime
FROM python:3.11-slim as runtime

WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    curl \
    libmagic1 \
    file \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY create_sample_survey_local.py /app/create_sample_survey_local.py

# Create non-root user and set permissions
RUN adduser --disabled-password --gecos '' --shell /bin/bash appuser \
    && chown -R appuser:appuser /app \
    && chmod +x /app/docker-entrypoint.sh

USER appuser

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Production command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
