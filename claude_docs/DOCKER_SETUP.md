# Docker Setup Guide

This guide explains how to run the TMG Market Research Platform using Docker Compose with automatic sample survey creation.

## Quick Start

### 1. Start the Application

```bash
docker-compose up --build
```

This will:
- 🗄️ Start PostgreSQL database
- 🚀 Build and start the backend (FastAPI)
- 🎨 Build and start the frontend (Next.js)
- 📦 Run database migrations automatically
- 🔨 Create a sample "Monster Energy" survey automatically

### 2. Access the Application

Once all services are running, you'll see:
```
✅ Sample survey created!
🎉 Backend is fully ready!
📝 Visit http://localhost:3000/survey/monster-lifestyle to see the sample survey
```

**URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Sample Survey: http://localhost:3000/survey/monster-lifestyle

## What Happens on Startup

The `docker-entrypoint.sh` script automatically:

1. **Waits for Database** - Ensures PostgreSQL is ready
2. **Runs Migrations** - Applies all Alembic database migrations
3. **Starts Backend** - Launches the FastAPI server
4. **Creates Sample Survey** - Runs `create_sample_survey_local.py`

### Sample Survey Details

The auto-created "Monster Energy" survey includes:

- **Personal Info Form**: Email, phone, region, date of birth, gender
- **Single Choice**: "How many times do you drink Monster Energy?"
- **Multiple Choice**: "What are your favorite flavors?"
- **Free Text**: "Explain why Monster helps you be at the top of your game"
- **Photo Upload**: Upload a photo of your Monster can (optional)
- **Video Upload**: Record a testimonial video (optional)

## Useful Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Database only
docker-compose logs -f db
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes (Clean Slate)

```bash
docker-compose down -v
```

This removes all data including the database. Next startup will create a fresh database with the sample survey.

### Rebuild After Code Changes

```bash
docker-compose up --build
```

### Access Backend Shell

```bash
docker-compose exec backend bash
```

### Access Database

```bash
docker-compose exec db psql -U user -d fastapi_db
```

## Environment Variables

The docker-compose.yml sets the following environment variables:

```yaml
DATABASE_URL: postgresql://user:password@db:5432/fastapi_db
DB_HOST: db
POSTGRES_USER: user
POSTGRES_PASSWORD: password
POSTGRES_DB: fastapi_db

# GCP Configuration (AI features enabled)
GCP_AI_ENABLED: "true"
GCP_PROJECT_ID: tmg-market-research
GCP_STORAGE_BUCKET_PHOTOS: tmg-market-research-photos
GCP_STORAGE_BUCKET_VIDEOS: tmg-market-research-videos
GOOGLE_APPLICATION_CREDENTIALS: /app/gcp-credentials.json

ALLOWED_ORIGINS: "http://localhost:3000"
```

### GCP AI Features

**Enabled by default!** The following AI features are active:

- 🖼️ **Vision API**: Analyzes uploaded photos for objects, text, labels
- 🎥 **Video Analysis**: Processes video uploads
- 🤖 **Gemini AI**: Generates descriptive labels (if GEMINI_API_KEY is set)
- ☁️ **Cloud Storage**: Uploads media to GCS buckets

**To use GCP AI, you need:**
1. ✅ GCP service account credentials (already mounted)
2. ✅ Active GCP project with billing enabled
3. ⚠️ Gemini API key (optional - add to `.env` file)

**Cost considerations:**
- Vision API: ~$1.50 per 1,000 images
- Gemini API: Varies by model and usage
- Cloud Storage: ~$0.02 per GB/month
- Small-scale testing: Usually < $1/day

### Configuring Gemini API (Optional)

To enable Gemini AI labeling, add your API key to `.env`:

```bash
# In the root .env file
GEMINI_API_KEY=your-gemini-api-key-here
```

Get a key at: https://makersuite.google.com/app/apikey

## Troubleshooting

### Sample Survey Already Exists

If you restart the services and see:
```
ℹ️  Survey 'monster-lifestyle' already exists, skipping creation
```

This is normal! The script detects the existing survey and skips creation.

### Backend Fails to Start

Check the logs:
```bash
docker-compose logs backend
```

Common issues:
- Database not ready: The entrypoint script waits up to 60 seconds
- Port 8000 in use: Stop other processes using port 8000
- Migration errors: Check database connection

### Frontend Fails to Build

```bash
docker-compose logs frontend
```

Common issues:
- Port 3000 in use: Stop other processes
- Node modules issues: Try `docker-compose build --no-cache frontend`

### GCP Credentials Issues

If you see errors like "could not find default credentials":

```bash
# Check if credentials file exists
ls -la backend/tmg-market-research-fd13d009581b.json

# Verify it's mounted in container
docker-compose exec backend ls -la /app/gcp-credentials.json

# Check environment variable
docker-compose exec backend env | grep GOOGLE_APPLICATION_CREDENTIALS
```

**Solution:**
- Ensure the JSON file exists in `backend/` directory
- Verify the volume mount in docker-compose.yml
- Check file permissions (should be readable)

### GCP API Not Enabled

If you see "API not enabled" errors:

```
Vision API has not been used in project [project-id]
```

**Solution:**
1. Go to https://console.cloud.google.com
2. Select your project: `tmg-market-research`
3. Enable these APIs:
   - Cloud Vision API
   - Cloud Storage API
   - Gemini API (optional)

### Disable GCP AI for Testing

If you want to disable GCP AI temporarily:

```yaml
# In docker-compose.yml, change:
GCP_AI_ENABLED: "false"
```

Then restart:
```bash
docker-compose restart backend
```

### Reset Everything

```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove old images
docker-compose rm -f

# Rebuild from scratch
docker-compose up --build
```

## Development Workflow

### Backend Development

The backend volume is mounted, so code changes are reflected immediately (with hot reload):

```yaml
volumes:
  - ./backend:/app
```

### Frontend Development

The frontend also has hot reload enabled:

```yaml
volumes:
  - ./frontend:/app
  - /app/node_modules  # Preserves node_modules
```

### Adding Custom Surveys

You can create additional surveys by:

1. Using the API directly:
```bash
curl -X POST http://localhost:8000/api/surveys/ \
  -H "Content-Type: application/json" \
  -d @my_survey.json
```

2. Creating a custom Python script similar to `create_sample_survey_local.py`

3. Using the frontend survey admin interface (if implemented)

## Production Considerations

This docker-compose setup is for **local development only**. For production:

1. Use environment variables from a `.env` file
2. Enable GCP AI services (`GCP_AI_ENABLED: "true"`)
3. Use a managed database service
4. Add authentication/authorization
5. Configure proper CORS origins
6. Use production-grade WSGI server settings
7. Enable HTTPS/SSL
8. Add proper logging and monitoring

## Files Reference

- `docker-compose.yml` - Service orchestration
- `backend/Dockerfile` - Backend container definition
- `backend/docker-entrypoint.sh` - Startup script
- `backend/create_sample_survey_local.py` - Sample survey creation
- `frontend/Dockerfile` - Frontend container definition
