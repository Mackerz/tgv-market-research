# Deploying to a New GCP Project

## Overview
This guide walks you through deploying the TMG Market Research application to a new Google Cloud Platform (GCP) project.

## Prerequisites

### 1. Create New GCP Project
1. Go to [GCP Console](https://console.cloud.google.com/)
2. Create a new project (e.g., `your-new-project-id`)
3. Note your project ID
4. Enable billing for the project

### 2. Enable Required APIs
```bash
# Set your new project
gcloud config set project YOUR-NEW-PROJECT-ID

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  sqladmin.googleapis.com \
  aiplatform.googleapis.com \
  vision.googleapis.com \
  videointelligence.googleapis.com
```

## Step 1: Create Infrastructure

### A. Create Cloud Storage Buckets

```bash
# Set your project ID
export PROJECT_ID="your-new-project-id"
export REGION="us-central1"

# Create buckets for media storage
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-survey-photos
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-survey-videos
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-question-media

# Set bucket permissions (public read if needed)
# gsutil iam ch allUsers:objectViewer gs://${PROJECT_ID}-survey-photos
# gsutil iam ch allUsers:objectViewer gs://${PROJECT_ID}-survey-videos
# gsutil iam ch allUsers:objectViewer gs://${PROJECT_ID}-question-media
```

### B. Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create tmg-market-research-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=$REGION \
  --root-password=CHANGE_THIS_PASSWORD \
  --storage-size=10GB \
  --storage-auto-increase

# Create database
gcloud sql databases create market_research \
  --instance=tmg-market-research-db

# Get connection string
gcloud sql instances describe tmg-market-research-db \
  --format='value(connectionName)'
```

### C. Create Service Account

```bash
# Create service account for the application
gcloud iam service-accounts create tmg-market-research \
  --display-name="TMG Market Research Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:tmg-market-research@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:tmg-market-research@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:tmg-market-research@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=tmg-market-research@${PROJECT_ID}.iam.gserviceaccount.com

# IMPORTANT: Keep this key secure and add to .gitignore
```

## Step 2: Configure Secrets in Secret Manager

```bash
# Database URL (format: postgresql://user:password@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE)
echo -n "postgresql://postgres:YOUR_PASSWORD@/market_research?host=/cloudsql/${PROJECT_ID}:${REGION}:tmg-market-research-db" | \
  gcloud secrets create database-url --data-file=-

# GCP Project ID
echo -n "$PROJECT_ID" | \
  gcloud secrets create gcp-project-id --data-file=-

# Storage Buckets
echo -n "${PROJECT_ID}-survey-photos" | \
  gcloud secrets create gcp-storage-bucket-photos --data-file=-

echo -n "${PROJECT_ID}-survey-videos" | \
  gcloud secrets create gcp-storage-bucket-videos --data-file=-

echo -n "${PROJECT_ID}-question-media" | \
  gcloud secrets create gcp-storage-bucket-question-media --data-file=-

# GCS Bucket Name (generic)
echo -n "${PROJECT_ID}-survey-photos" | \
  gcloud secrets create gcs-bucket-name --data-file=-

# Enable storage
echo -n "true" | \
  gcloud secrets create gcp-storage-enabled --data-file=-

# Enable AI
echo -n "true" | \
  gcloud secrets create gcp-ai-enabled --data-file=-

# JWT Secret Key (generate a secure one)
python3 -c "import secrets; print(secrets.token_hex(32))" | \
  gcloud secrets create secret-key --data-file=-

# API Key (for admin access)
python3 -c "import secrets; print(secrets.token_hex(32))" | \
  gcloud secrets create api-key --data-file=-

# Google OAuth credentials (get from Google Cloud Console)
echo -n "YOUR_GOOGLE_CLIENT_ID" | \
  gcloud secrets create google-client-id --data-file=-

echo -n "YOUR_GOOGLE_CLIENT_SECRET" | \
  gcloud secrets create google-client-secret --data-file=-

# Gemini API Key (if using Gemini)
echo -n "YOUR_GEMINI_API_KEY" | \
  gcloud secrets create gemini-api-key --data-file=-

# CORS allowed origins
echo -n "https://your-frontend-domain.com,https://your-new-project-frontend-xxxxx-uc.a.run.app" | \
  gcloud secrets create allowed-origins --data-file=-
```

## Step 3: Update Configuration Files

### A. Update `cloudbuild.yaml`

The main `cloudbuild.yaml` uses `$PROJECT_ID` which is automatically injected by Cloud Build.
However, you need to update:

1. **Line 69** - Update the backend URL after first deployment:
```yaml
- '--set-env-vars=NEXT_PUBLIC_API_URL=https://tmg-market-research-backend-YOUR_PROJECT_HASH.run.app'
```

2. **Line 51** - Add any new secrets you created:
```yaml
--set-secrets=DATABASE_URL=database-url:latest,
  GCP_PROJECT_ID=gcp-project-id:latest,
  GCS_BUCKET_NAME=gcs-bucket-name:latest,
  GCP_STORAGE_BUCKET_PHOTOS=gcp-storage-bucket-photos:latest,
  GCP_STORAGE_BUCKET_VIDEOS=gcp-storage-bucket-videos:latest,
  GCP_STORAGE_BUCKET_QUESTION_MEDIA=gcp-storage-bucket-question-media:latest,
  GCP_STORAGE_ENABLED=gcp-storage-enabled:latest,
  GCP_AI_ENABLED=gcp-ai-enabled:latest,
  SECRET_KEY=secret-key:latest,
  API_KEY=api-key:latest,
  GOOGLE_CLIENT_ID=google-client-id:latest,
  GOOGLE_CLIENT_SECRET=google-client-secret:latest,
  GEMINI_API_KEY=gemini-api-key:latest,
  ALLOWED_ORIGINS=allowed-origins:latest
```

### B. Update `frontend/cloudbuild.yaml`

Update line 6 and 8 with your new project:
```yaml
- --build-arg=NEXT_PUBLIC_API_URL=https://tmg-market-research-backend-YOUR_HASH.run.app
- gcr.io/YOUR-NEW-PROJECT-ID/tmg-market-research-frontend-fixed
```

## Step 4: Deploy Application

### A. Connect Repository to Cloud Build

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click "Connect Repository"
3. Select GitHub and authenticate
4. Choose your repository: `Mackerz/tgv-market-research`
5. Create a trigger:
   - Name: `deploy-main`
   - Event: Push to branch
   - Branch: `^main$`
   - Configuration: `cloudbuild.yaml`

### B. Manual Deploy (First Time)

```bash
# Submit build manually
gcloud builds submit --config=cloudbuild.yaml .

# Or trigger via git push
git push origin main
```

### C. Get Backend URL

After backend deploys:
```bash
gcloud run services describe tmg-market-research-backend \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### D. Update Frontend with Backend URL

Update `cloudbuild.yaml` line 69 with the backend URL from above, then redeploy.

## Step 5: Post-Deployment Configuration

### A. Run Database Migrations

```bash
# Connect to Cloud Run backend
gcloud run services proxy tmg-market-research-backend --port=8000

# Or use Cloud Shell to run migrations
# (This assumes your backend container runs migrations on startup via docker-entrypoint.sh)
```

### B. Create Sample Data (Optional)

```bash
# If needed, exec into backend container
gcloud run services proxy tmg-market-research-backend --port=8000 &
curl http://localhost:8000/api/health

# Or use the create_sample_survey.py script
```

### C. Update Google OAuth

Update your Google OAuth consent screen with the new Cloud Run URLs:
- Authorized JavaScript origins: `https://your-frontend-url.run.app`
- Authorized redirect URIs: `https://your-frontend-url.run.app`

## Step 6: Verify Deployment

```bash
# Check backend health
BACKEND_URL=$(gcloud run services describe tmg-market-research-backend \
  --platform managed --region us-central1 --format 'value(status.url)')
curl $BACKEND_URL/api/health

# Check frontend
FRONTEND_URL=$(gcloud run services describe tmg-market-research-frontend \
  --platform managed --region us-central1 --format 'value(status.url)')
echo "Frontend: $FRONTEND_URL"
```

## Step 7: Custom Domain (Optional)

```bash
# Map custom domain to Cloud Run
gcloud run domain-mappings create \
  --service tmg-market-research-frontend \
  --domain your-domain.com \
  --region us-central1
```

## Troubleshooting

### Check Logs
```bash
# Backend logs
gcloud run services logs read tmg-market-research-backend \
  --platform managed \
  --region us-central1

# Frontend logs
gcloud run services logs read tmg-market-research-frontend \
  --platform managed \
  --region us-central1

# Build logs
gcloud builds log $(gcloud builds list --limit=1 --format='value(id)')
```

### Common Issues

1. **Database Connection Failed**: Check Cloud SQL instance is running and connection string is correct
2. **Storage Bucket Access Denied**: Verify service account has `storage.objectAdmin` role
3. **Frontend Can't Reach Backend**: Update CORS settings in `allowed-origins` secret
4. **Build Fails**: Check all required APIs are enabled

## Cost Optimization

- **Cloud Run**: Uses pay-per-request pricing (free tier: 2M requests/month)
- **Cloud SQL**: Consider using `db-f1-micro` for low traffic
- **Cloud Storage**: Standard storage class, consider lifecycle policies
- **Set min-instances=0**: Scale to zero when not in use

## Security Checklist

- [ ] All secrets stored in Secret Manager (not in code)
- [ ] Service account has minimum necessary permissions
- [ ] Cloud SQL uses private IP (if needed)
- [ ] CORS configured with specific origins (no wildcards)
- [ ] API keys rotated regularly
- [ ] Bucket permissions reviewed (public vs private)
- [ ] Enable Cloud Armor for DDoS protection (if needed)

## Next Steps

1. Set up monitoring and alerting
2. Configure Cloud Logging
3. Set up backup strategy for Cloud SQL
4. Consider using Cloud CDN for frontend
5. Implement CI/CD pipeline improvements

## Estimated Costs

For a low-traffic application:
- **Cloud Run**: $5-20/month
- **Cloud SQL (f1-micro)**: $9/month
- **Cloud Storage**: $0.02/GB/month
- **Total**: ~$15-30/month

For higher traffic, costs scale with usage.
