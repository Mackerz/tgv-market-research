#!/bin/bash

# TMG Market Research - New GCP Project Setup Script
# This script automates the setup of infrastructure in a new GCP project

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Prompt for project details
echo "=========================================="
echo "TMG Market Research - GCP Project Setup"
echo "=========================================="
echo ""

read -p "Enter your NEW GCP Project ID: " PROJECT_ID
read -p "Enter region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

read -p "Enter Cloud SQL password: " -s SQL_PASSWORD
echo ""

# Confirm
echo ""
print_info "Project ID: $PROJECT_ID"
print_info "Region: $REGION"
echo ""
read -p "Is this correct? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Setup cancelled"
    exit 1
fi

# Set project
print_info "Setting active project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable APIs
print_info "Enabling required APIs (this may take a few minutes)..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  sqladmin.googleapis.com \
  aiplatform.googleapis.com \
  vision.googleapis.com \
  videointelligence.googleapis.com \
  --quiet

print_info "✓ APIs enabled"

# Create Storage Buckets
print_info "Creating Cloud Storage buckets..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-survey-photos || print_warn "Bucket may already exist"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-survey-videos || print_warn "Bucket may already exist"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-question-media || print_warn "Bucket may already exist"
print_info "✓ Storage buckets created"

# Create Cloud SQL instance
print_info "Creating Cloud SQL PostgreSQL instance (this takes 5-10 minutes)..."
if gcloud sql instances describe tmg-market-research-db &> /dev/null; then
    print_warn "Cloud SQL instance already exists, skipping creation"
else
    gcloud sql instances create tmg-market-research-db \
      --database-version=POSTGRES_15 \
      --tier=db-f1-micro \
      --region=$REGION \
      --root-password="$SQL_PASSWORD" \
      --storage-size=10GB \
      --storage-auto-increase \
      --quiet

    print_info "Creating database 'market_research'..."
    gcloud sql databases create market_research \
      --instance=tmg-market-research-db \
      --quiet
fi

# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe tmg-market-research-db --format='value(connectionName)')
print_info "✓ Cloud SQL instance ready: $CONNECTION_NAME"

# Create Service Account
print_info "Creating service account..."
if gcloud iam service-accounts describe tmg-market-research@${PROJECT_ID}.iam.gserviceaccount.com &> /dev/null; then
    print_warn "Service account already exists, skipping creation"
else
    gcloud iam service-accounts create tmg-market-research \
      --display-name="TMG Market Research Service Account" \
      --quiet

    # Grant permissions
    print_info "Granting IAM permissions..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:tmg-market-research@${PROJECT_ID}.iam.gserviceaccount.com" \
      --role="roles/storage.objectAdmin" \
      --quiet

    gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:tmg-market-research@${PROJECT_ID}.iam.gserviceaccount.com" \
      --role="roles/cloudsql.client" \
      --quiet

    gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:tmg-market-research@${PROJECT_ID}.iam.gserviceaccount.com" \
      --role="roles/aiplatform.user" \
      --quiet
fi
print_info "✓ Service account configured"

# Generate secrets
print_info "Generating secrets..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
API_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create secrets
print_info "Creating secrets in Secret Manager..."

# Database URL
DB_URL="postgresql://postgres:${SQL_PASSWORD}@/market_research?host=/cloudsql/${CONNECTION_NAME}"
echo -n "$DB_URL" | gcloud secrets create database-url --data-file=- --quiet 2>/dev/null || \
  echo -n "$DB_URL" | gcloud secrets versions add database-url --data-file=- --quiet

# Project ID
echo -n "$PROJECT_ID" | gcloud secrets create gcp-project-id --data-file=- --quiet 2>/dev/null || \
  echo -n "$PROJECT_ID" | gcloud secrets versions add gcp-project-id --data-file=- --quiet

# Storage buckets
echo -n "${PROJECT_ID}-survey-photos" | gcloud secrets create gcp-storage-bucket-photos --data-file=- --quiet 2>/dev/null || \
  echo -n "${PROJECT_ID}-survey-photos" | gcloud secrets versions add gcp-storage-bucket-photos --data-file=- --quiet

echo -n "${PROJECT_ID}-survey-videos" | gcloud secrets create gcp-storage-bucket-videos --data-file=- --quiet 2>/dev/null || \
  echo -n "${PROJECT_ID}-survey-videos" | gcloud secrets versions add gcp-storage-bucket-videos --data-file=- --quiet

echo -n "${PROJECT_ID}-question-media" | gcloud secrets create gcp-storage-bucket-question-media --data-file=- --quiet 2>/dev/null || \
  echo -n "${PROJECT_ID}-question-media" | gcloud secrets versions add gcp-storage-bucket-question-media --data-file=- --quiet

echo -n "${PROJECT_ID}-survey-photos" | gcloud secrets create gcs-bucket-name --data-file=- --quiet 2>/dev/null || \
  echo -n "${PROJECT_ID}-survey-photos" | gcloud secrets versions add gcs-bucket-name --data-file=- --quiet

# Enable flags
echo -n "true" | gcloud secrets create gcp-storage-enabled --data-file=- --quiet 2>/dev/null || \
  echo -n "true" | gcloud secrets versions add gcp-storage-enabled --data-file=- --quiet

echo -n "true" | gcloud secrets create gcp-ai-enabled --data-file=- --quiet 2>/dev/null || \
  echo -n "true" | gcloud secrets versions add gcp-ai-enabled --data-file=- --quiet

# Auth secrets
echo -n "$SECRET_KEY" | gcloud secrets create secret-key --data-file=- --quiet 2>/dev/null || \
  echo -n "$SECRET_KEY" | gcloud secrets versions add secret-key --data-file=- --quiet

echo -n "$API_KEY" | gcloud secrets create api-key --data-file=- --quiet 2>/dev/null || \
  echo -n "$API_KEY" | gcloud secrets versions add api-key --data-file=- --quiet

print_info "✓ Secrets created"

# Output summary
echo ""
echo "=========================================="
print_info "Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Cloud SQL: $CONNECTION_NAME"
echo "  Storage Buckets:"
echo "    - ${PROJECT_ID}-survey-photos"
echo "    - ${PROJECT_ID}-survey-videos"
echo "    - ${PROJECT_ID}-question-media"
echo ""
echo "🔑 Generated Credentials (SAVE THESE!):"
echo "  API Key: $API_KEY"
echo "  Secret Key: $SECRET_KEY"
echo ""
echo "⚠️  Next Steps:"
echo "  1. Configure Google OAuth credentials:"
echo "     https://console.cloud.google.com/apis/credentials"
echo "     Then add secrets: google-client-id, google-client-secret"
echo ""
echo "  2. If using Gemini AI, add secret: gemini-api-key"
echo ""
echo "  3. Update cloudbuild.yaml with your backend URL (after first deploy)"
echo ""
echo "  4. Deploy the application:"
echo "     gcloud builds submit --config=cloudbuild.yaml ."
echo ""
echo "  5. Get your service URLs:"
echo "     gcloud run services list --platform managed --region $REGION"
echo ""
print_info "For detailed documentation, see DEPLOYMENT_NEW_PROJECT.md"
