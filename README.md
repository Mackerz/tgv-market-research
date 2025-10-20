# TMG Market Research Platform

A modern full-stack market research survey platform with AI-powered media analysis, built with Next.js, FastAPI, PostgreSQL, and Google Cloud Platform integrations.

## Overview

TMG Market Research is a comprehensive survey platform that enables:
- **Dynamic Survey Creation** - Build custom surveys with multiple question types
- **Media Collection** - Photo and video submissions from respondents
- **AI-Powered Analysis** - Automatic media analysis using Google Cloud Vision, Video Intelligence, and Gemini
- **Real-time Reporting** - Interactive dashboards with demographics and response analytics
- **Approval Workflow** - Review and approve/reject submissions before including in reports

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Next.js   │────────▶│   FastAPI   │────────▶│ PostgreSQL   │
│  Frontend   │         │   Backend   │         │   Database   │
│   :3000     │         │    :8000    │         │    :5432     │
└─────────────┘         └─────────────┘         └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   GCP APIs   │
                        ├──────────────┤
                        │ Cloud Storage│
                        │ Vision API   │
                        │ Video Intel  │
                        │ Gemini AI    │
                        └──────────────┘
```

## Project Structure

```
.
├── frontend/                     # Next.js 14 application
│   ├── src/
│   │   ├── app/                 # App router pages
│   │   │   ├── page.tsx        # Home/Survey list
│   │   │   ├── survey/[slug]/  # Survey response flow
│   │   │   └── report/[slug]/  # Reporting dashboard
│   │   ├── components/         # React components
│   │   └── lib/                # Utilities and API client
│   ├── Dockerfile
│   └── package.json
│
├── backend/                      # FastAPI application
│   ├── app/                     # Main application package
│   │   ├── api/v1/             # API route modules
│   │   │   ├── users.py        # User management
│   │   │   ├── surveys.py      # Survey CRUD
│   │   │   ├── submissions.py  # Survey submissions
│   │   │   ├── media.py        # Media analysis
│   │   │   ├── reporting.py    # Reports & analytics
│   │   │   └── settings.py     # Report settings
│   │   ├── core/               # Core functionality
│   │   │   └── database.py     # SQLAlchemy config
│   │   ├── crud/               # Database operations
│   │   │   ├── base.py         # Generic CRUD base
│   │   │   ├── user.py
│   │   │   ├── survey.py
│   │   │   ├── media.py
│   │   │   ├── reporting.py
│   │   │   └── settings.py
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── survey.py
│   │   │   ├── media.py
│   │   │   └── settings.py
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── survey.py
│   │   │   ├── media.py
│   │   │   ├── reporting.py
│   │   │   └── settings.py
│   │   ├── integrations/       # External services
│   │   │   └── gcp/           # Google Cloud Platform
│   │   │       ├── storage.py  # Cloud Storage
│   │   │       ├── vision.py   # Vision/Video API
│   │   │       ├── gemini.py   # Gemini AI
│   │   │       └── secrets.py  # Secret Manager
│   │   ├── services/           # Business logic
│   │   │   ├── media_analysis.py
│   │   │   └── media_proxy.py
│   │   ├── utils/              # Helper functions
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   └── main.py            # Application entry point
│   ├── alembic/                # Database migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run-migrations.py
│
├── docker-compose.yml           # Container orchestration
└── README.md                    # This file
```

## Key Features

### 1. Survey Management
- Create surveys with custom questions
- Multiple question types: single choice, multiple choice, free text, photo, video
- Survey flow customization
- Active/inactive status control
- Client organization support

### 2. Response Collection
- Mobile-friendly survey interface
- Photo and video upload to GCP Cloud Storage
- Progress tracking
- Demographic data collection (age, gender, region)
- Submission completion workflow

### 3. AI-Powered Media Analysis
- **Photo Analysis** (Google Vision API):
  - Object detection
  - Text recognition (OCR)
  - Brand detection
  - Safe search filtering

- **Video Analysis** (Google Video Intelligence):
  - Object tracking
  - Speech-to-text transcription
  - Shot detection
  - Label detection

- **Gemini AI Labeling**:
  - Context-aware categorization
  - Theme extraction
  - Sentiment analysis
  - Multi-language support

### 4. Reporting & Analytics
- Submission approval workflow (approve/reject/pending)
- Demographics breakdown (age ranges, gender, region)
- Response aggregation by question type
- Media gallery with filtering
- Label frequency analysis
- Interactive charts and visualizations
- Export capabilities

### 5. Settings Management
- Custom age range definitions
- Question display name customization
- Report configuration per survey

## Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Heroicons** - Icon library

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM with PostgreSQL
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Python 3.11** - Latest Python features

### Database
- **PostgreSQL 15** - Relational database
- Complex relationships (surveys → submissions → responses → media)
- JSON columns for flexible data storage

### Cloud Services (GCP)
- **Cloud Storage** - Photo/video file storage
- **Vision API** - Image analysis
- **Video Intelligence** - Video analysis
- **Gemini AI** - Advanced text analysis
- **Secret Manager** - Secure credential storage

### DevOps
- **Docker & Docker Compose** - Containerization
- **Cloud Run** - Serverless deployment
- **Cloud Build** - CI/CD pipeline

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- GCP project with enabled APIs
- Service account key (`tmg-market-research-fd13d009581b.json`)

### 1. Environment Setup

Create `backend/.env`:
```bash
DATABASE_URL=postgresql://user:password@db:5432/marketresearch
GOOGLE_APPLICATION_CREDENTIALS=/app/tmg-market-research-fd13d009581b.json
GCP_AI_ENABLED=true
GEMINI_ENABLED=true
```

### 2. Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

### 3. Run Database Migrations

```bash
docker-compose exec backend python run-migrations.py
```

### 4. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

## Development Setup

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## API Endpoints

### Survey Management
- `POST /api/surveys/` - Create survey
- `GET /api/surveys/` - List surveys (with filtering/search)
- `GET /api/surveys/{id}` - Get survey details
- `GET /api/surveys/slug/{slug}` - Get survey by slug
- `PUT /api/surveys/{id}` - Update survey
- `DELETE /api/surveys/{id}` - Delete survey

### Submissions
- `POST /api/surveys/{slug}/submit` - Create submission
- `GET /api/submissions/{id}` - Get submission
- `GET /api/submissions/{id}/progress` - Get progress
- `PUT /api/submissions/{id}/complete` - Mark complete

### Responses
- `POST /api/submissions/{id}/responses` - Add response
- `GET /api/submissions/{id}/responses` - List responses

### File Uploads
- `POST /api/surveys/{slug}/upload/photo` - Upload photo
- `POST /api/surveys/{slug}/upload/video` - Upload video

### Reporting
- `GET /api/reports/{slug}/submissions` - Get submissions list
- `GET /api/reports/{slug}/submissions/{id}` - Get submission details
- `PUT /api/reports/{slug}/submissions/{id}/approve` - Approve submission
- `PUT /api/reports/{slug}/submissions/{id}/reject` - Reject submission
- `GET /api/reports/{slug}/data` - Get report data
- `GET /api/reports/{slug}/media-gallery` - Get media gallery

### Media Analysis
- `GET /api/responses/{id}/media-analysis` - Get analysis results
- `POST /api/responses/{id}/trigger-analysis` - Manually trigger analysis
- `GET /api/surveys/{id}/reporting-labels` - Get label summary
- `GET /api/media/proxy` - Proxy media files (supports video streaming)

### Settings
- `GET /api/reports/{slug}/settings` - Get report settings
- `PUT /api/reports/{slug}/settings/age-ranges` - Update age ranges
- `PUT /api/reports/{slug}/settings/question-display-names` - Bulk update names

## Database Models

### User & Post (Demo/Template)
- User model with email, username, full_name
- Post model with user relationship
- Timestamps and soft deletes

### Survey Domain
- **Survey**: Survey definition with flow configuration
- **Submission**: User submission with demographics
- **Response**: Individual question responses with media URLs
- **Media**: AI analysis results (descriptions, transcripts, labels, brands)

### Settings Domain
- **ReportSettings**: Survey-level settings (age ranges)
- **QuestionDisplayName**: Custom question labels for reports

## Code Architecture

### Design Patterns

1. **CRUD Base Pattern**
   - Generic `CRUDBase` class for common operations
   - Type-safe with Python Generics
   - Eliminates code duplication

2. **Dependency Injection**
   - FastAPI dependency system
   - Reusable validation helpers
   - Consistent error handling

3. **Service Layer**
   - Business logic separated from routes
   - Testable components
   - GCP integration abstraction

4. **Modular Routes**
   - Domain-specific route modules
   - Clean separation of concerns
   - Single Responsibility Principle

### Recent Improvements (Phase 1 Refactor)

✅ **API Router Split** - Reduced main.py from 846 to 82 lines (90% reduction)
✅ **CRUD Refactor** - Eliminated 98 lines of duplicate CRUD logic
✅ **Dependency Expansion** - Eliminated 40+ lines of duplicate 404 patterns
✅ **Legacy Cleanup** - Removed 21 orphaned legacy files

See detailed documentation:
- `/backend/API_ROUTER_REFACTOR_SUMMARY.md`
- `/backend/CRUD_BASE_REFACTOR_SUMMARY.md`
- `/backend/DEPENDENCY_REFACTOR_SUMMARY.md`
- `/backend/LEGACY_CLEANUP_SUMMARY.md`

## GCP Configuration

### Required APIs
- Cloud Storage API
- Cloud Vision API
- Cloud Video Intelligence API
- Vertex AI API (Gemini)
- Secret Manager API

### GCS Buckets
- `tmg-market-research-photos` - Photo uploads
- `tmg-market-research-videos` - Video uploads

### Secrets
- `database-url` - PostgreSQL connection string
- `gemini-api-key` - Gemini AI API key
- `allowed-origins` - CORS allowed origins

## Deployment

### Google Cloud Run

The application is deployed on Cloud Run using:

```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml

# View logs
gcloud logs read --service=tmg-market-research-backend --limit 50
```

### Environment Variables (Cloud Run)

Set via Secret Manager or environment variables:
- `DATABASE_URL` - PostgreSQL connection (Cloud SQL)
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account (automatic)
- `GCP_AI_ENABLED` - Enable AI features (true/false)
- `GEMINI_ENABLED` - Enable Gemini labeling (true/false)
- `ALLOWED_ORIGINS` - CORS origins

## Testing

### API Testing

Use the interactive docs:
```
http://localhost:8000/docs
```

Or test with curl:
```bash
# Health check
curl http://localhost:8000/api/health

# Create user
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser"}'
```

### Frontend Testing

```bash
cd frontend
npm run test       # Run tests
npm run lint       # Run linter
npm run build      # Production build
```

## Common Tasks

### Create a New Survey

```bash
curl -X POST http://localhost:8000/api/surveys/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Feedback Survey",
    "client": "ACME Corp",
    "survey_flow": [
      {
        "id": "q1",
        "question": "Rate our product",
        "question_type": "single_choice",
        "options": ["Excellent", "Good", "Fair", "Poor"]
      }
    ]
  }'
```

### View Media Analysis

```bash
# Get analysis for a response
curl http://localhost:8000/api/responses/123/media-analysis
```

### Approve Submissions

```bash
# Approve a submission
curl -X PUT http://localhost:8000/api/reports/{survey_slug}/submissions/123/approve
```

## What You Get

✅ Complete survey platform with dynamic question types
✅ AI-powered media analysis (Vision, Video Intelligence, Gemini)
✅ Real-time reporting with demographics and analytics
✅ Modern React frontend with TypeScript
✅ High-performance FastAPI backend
✅ SQLAlchemy ORM with PostgreSQL
✅ Database migrations with Alembic
✅ Full CRUD operations with type validation
✅ GCP integration (Storage, AI APIs, Secret Manager)
✅ Docker containerization
✅ Cloud Run deployment ready
✅ Interactive API documentation
✅ Modular, maintainable code architecture

## License

Proprietary - TMG Market Research Platform

## Support

For issues or questions, contact the development team.
