#!/bin/bash
set -e

echo "🚀 Starting backend container..."

# Ensure virtual environment is in PATH
export PATH="/app/.venv/bin:$PATH"
export PYTHONPATH="/app:$PYTHONPATH"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "⏳ Database is unavailable - sleeping"
  sleep 2
done

echo "✅ Database is ready!"

# Run database migrations
echo "📦 Running database migrations..."
cd /app
/app/.venv/bin/alembic upgrade head

echo "✅ Migrations complete!"

# Wait a bit for backend to fully initialize
echo "⏳ Starting backend server..."
/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend API to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0
until curl -s http://localhost:8000/api/health > /dev/null 2>&1; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ Backend failed to start after $MAX_RETRIES attempts"
    exit 1
  fi
  echo "⏳ Backend not ready yet (attempt $RETRY_COUNT/$MAX_RETRIES)..."
  sleep 2
done

echo "✅ Backend is ready!"

# Create sample survey
echo "🔨 Creating sample survey..."
cd /app
/app/.venv/bin/python /app/create_sample_survey_local.py

echo "✅ Sample survey created!"
echo "🎉 Backend is fully ready!"
echo "📝 Visit http://localhost:3000/survey/monster-lifestyle to see the sample survey"

# Keep backend running in foreground
wait $BACKEND_PID
