# Quick Deployment Reference

## Prerequisites
```bash
gcloud auth login
gcloud auth configure-docker
```

## One-Command Deployment

### 1. Set your project ID
```bash
export PROJECT_ID="your-project-id"
```

### 2. Run deployment scripts
```bash
# Set up database
./setup-database.sh $PROJECT_ID

# Deploy applications
./deploy.sh $PROJECT_ID
```

### 3. Configure additional secrets (optional)
```bash
# Set up additional secrets like Gemini API key, GCS bucket
./setup-secrets.sh $PROJECT_ID

# Database credentials are automatically stored by setup-database.sh
# Your backend will automatically use secrets from Secret Manager
```

### 4. Run migrations
```bash
# Create migration job (uses Secret Manager automatically)
gcloud run jobs create tmg-migration-job \
  --image=gcr.io/$PROJECT_ID/tmg-market-research-backend \
  --region=us-central1 \
  --set-secrets="DATABASE_URL=database-url:latest,GCP_PROJECT_ID=gcp-project-id:latest" \
  --command="python" \
  --args="run-migrations.py"

# Execute migration
gcloud run jobs execute tmg-migration-job --region=us-central1
```

## Useful Commands

### View Service Status
```bash
gcloud run services list --region=us-central1
```

### View Logs
```bash
gcloud run services logs read tmg-market-research-backend --region=us-central1 --limit=50
```

### Update Service with Secrets
```bash
# Add new secret
echo -n "secret-value" | gcloud secrets create secret-name --data-file=-

# Update service to use new secret
gcloud run services update tmg-market-research-backend \
  --region=us-central1 \
  --set-secrets="SECRET_NAME=secret-name:latest"
```

### Manage Secrets
```bash
# List secrets
gcloud secrets list

# View secret value
gcloud secrets versions access latest --secret="secret-name"
```

### Delete Services
```bash
gcloud run services delete tmg-market-research-backend --region=us-central1
gcloud run services delete tmg-market-research-frontend --region=us-central1
```

## URLs After Deployment
- Backend: `https://tmg-market-research-backend-HASH-uc.a.run.app`
- Frontend: `https://tmg-market-research-frontend-HASH-uc.a.run.app`