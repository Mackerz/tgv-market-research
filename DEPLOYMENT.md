# TMG Market Research - GCP Cloud Run Deployment Guide

This guide will help you deploy the TMG Market Research application to Google Cloud Platform using Cloud Run.

## Prerequisites

1. **Google Cloud Platform Account**
   - Active GCP project with billing enabled
   - Owner or Editor permissions

2. **Required Tools**
   - [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
   - Docker (optional, for local testing)
   - Git

3. **Authentication**
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

## Quick Start

### 1. Clone and Navigate to Project
```bash
git clone <your-repo-url>
cd marketResearch
```

### 2. Set Up Database
```bash
# Make the script executable
chmod +x setup-database.sh

# Run database setup (replace YOUR_PROJECT_ID with your actual project ID)
./setup-database.sh YOUR_PROJECT_ID us-central1
```

This script will:
- Create a Cloud SQL PostgreSQL instance
- Set up database users and permissions
- Provide connection details for your application

### 3. Deploy Applications
```bash
# Make the script executable
chmod +x deploy.sh

# Deploy both backend and frontend (replace YOUR_PROJECT_ID)
./deploy.sh YOUR_PROJECT_ID us-central1
```

This script will:
- Build and push Docker images to Container Registry
- Deploy backend and frontend to Cloud Run
- Provide URLs for both services

### 4. Set Up Additional Secrets (Optional)

The database setup automatically stores database credentials in Secret Manager. You can add additional secrets:

```bash
# Set up additional secrets like Gemini API key, GCS bucket, etc.
./setup-secrets.sh YOUR_PROJECT_ID
```

This will prompt you to enter:
- Gemini API Key (for AI analysis)
- GCS Bucket Name (for media storage)
- CORS Origins (for frontend access)

**Note**: Database credentials are automatically stored by the database setup script.

### 5. Run Database Migrations

Create a Cloud Run job to run migrations (uses Secret Manager automatically):

```bash
gcloud run jobs create tmg-migration-job \
  --image=gcr.io/YOUR_PROJECT_ID/tmg-market-research-backend \
  --region=us-central1 \
  --set-secrets="DATABASE_URL=database-url:latest,GCP_PROJECT_ID=gcp-project-id:latest" \
  --command="python" \
  --args="run-migrations.py"

# Execute the migration
gcloud run jobs execute tmg-migration-job --region=us-central1
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   Database      │
│  (Next.js)      │───▶│   (FastAPI)      │───▶│  (Cloud SQL)    │
│  Cloud Run      │    │   Cloud Run      │    │  PostgreSQL     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Services Overview

### Backend Service (`tmg-market-research-backend`)
- **Framework**: FastAPI with Python 3.11
- **Database**: PostgreSQL via Cloud SQL
- **Storage**: Google Cloud Storage for media files
- **AI**: Google Cloud Vision, Video Intelligence, and Gemini API
- **Port**: 8000
- **Resources**: 1 vCPU, 1GB RAM

### Frontend Service (`tmg-market-research-frontend`)
- **Framework**: Next.js 15 with React 19
- **Styling**: Tailwind CSS
- **Port**: 3000
- **Resources**: 1 vCPU, 512MB RAM

### Database
- **Type**: Cloud SQL PostgreSQL 15
- **Tier**: db-f1-micro (upgradeable)
- **Storage**: 10GB SSD (auto-expandable)

## Secret Management

This deployment uses **Google Cloud Secret Manager** for secure credential storage. No sensitive information is stored in environment variables.

### Automatically Managed Secrets
These secrets are created automatically by the setup scripts:

| Secret Name | Description | Created By |
|-------------|-------------|------------|
| `database-url` | Complete database connection string | `setup-database.sh` |
| `db-password` | Database password | `setup-database.sh` |
| `db-host` | Database host IP | `setup-database.sh` |
| `db-name` | Database name | `setup-database.sh` |
| `db-user` | Database username | `setup-database.sh` |
| `gcp-project-id` | GCP Project ID | `setup-database.sh` |

### Optional Secrets
Set these manually using `setup-secrets.sh`:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `gemini-api-key` | Gemini AI API key | Optional |
| `gcs-bucket-name` | GCS bucket for media storage | Optional |
| `allowed-origins` | CORS allowed origins | Recommended |

### Non-Secret Environment Variables
```bash
# These can remain as environment variables (not sensitive)
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Frontend Environment Variables
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.app
NODE_ENV=production
```

## Manual Deployment Steps

If you prefer manual deployment over using the scripts:

### 1. Enable APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

### 2. Build and Push Images
```bash
# Backend
gcloud builds submit ./backend --tag gcr.io/YOUR_PROJECT/tmg-market-research-backend

# Frontend
gcloud builds submit ./frontend --tag gcr.io/YOUR_PROJECT/tmg-market-research-frontend
```

### 3. Deploy Services
```bash
# Backend
gcloud run deploy tmg-market-research-backend \
  --image gcr.io/YOUR_PROJECT/tmg-market-research-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --port 8000

# Frontend
gcloud run deploy tmg-market-research-frontend \
  --image gcr.io/YOUR_PROJECT/tmg-market-research-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --port 3000
```

## Security Considerations

1. **Database Security**
   - Use strong passwords
   - Consider private IP for database
   - Enable backup and point-in-time recovery

2. **Application Security**
   - Configure proper CORS origins
   - Use service accounts for GCP services
   - Implement proper authentication if needed

3. **Network Security**
   - Consider using a VPC
   - Implement Cloud Armor for DDoS protection

## Monitoring and Logging

- **Cloud Run Logs**: Available in Cloud Console
- **Application Logs**: Structured logging with Python logging
- **Database Monitoring**: Cloud SQL monitoring dashboard
- **Alerting**: Set up alerts for service errors and database performance

## Scaling

### Automatic Scaling
Both services are configured with:
- **Minimum instances**: 0 (scale to zero)
- **Maximum instances**: Backend (10), Frontend (5)
- **Auto-scaling**: Based on request volume and CPU usage

### Manual Scaling
```bash
# Update backend scaling
gcloud run services update tmg-market-research-backend \
  --region us-central1 \
  --min-instances 1 \
  --max-instances 20
```

## Cost Optimization

1. **Scale to Zero**: Services scale to 0 when not in use
2. **Right-sizing**: Adjust CPU/memory based on usage patterns
3. **Database**: Use smallest instance size that meets performance needs
4. **Storage**: Configure lifecycle policies for GCS

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database status
   gcloud sql instances describe tmg-market-research-db

   # Test connection
   gcloud sql connect tmg-market-research-db --user=app_user
   ```

2. **Service Not Starting**
   ```bash
   # View service logs
   gcloud run services logs read tmg-market-research-backend --region us-central1
   ```

3. **Build Failures**
   ```bash
   # Check build logs
   gcloud builds log BUILD_ID
   ```

### Health Checks
- Backend health: `https://your-backend-url.app/`
- Frontend health: `https://your-frontend-url.app/`

## CI/CD with Cloud Build

The included `cloudbuild.yaml` enables automatic deployments:

1. Connect your repository to Cloud Build
2. Create triggers for automatic deployment on push
3. Configure build variables in Cloud Build settings

## Support

For deployment issues:
1. Check Cloud Run service logs
2. Verify environment variables
3. Test database connectivity
4. Review security policies and IAM permissions

---

**Next Steps**: After successful deployment, consider setting up monitoring, alerting, and backup strategies for your production environment.