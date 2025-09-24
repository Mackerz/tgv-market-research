#!/bin/bash

# TMG Market Research - GCP Cloud Run Deployment Script
# This script deploys both backend and frontend to Google Cloud Run

set -e  # Exit on any error

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
BACKEND_SERVICE="tmg-market-research-backend"
FRONTEND_SERVICE="tmg-market-research-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo_error "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if project ID is provided
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo_error "Please provide your GCP project ID as the first argument"
    echo "Usage: ./deploy.sh YOUR_PROJECT_ID [REGION]"
    exit 1
fi

echo_info "Starting deployment to GCP Project: $PROJECT_ID"
echo_info "Region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo_info "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Build and push backend image
echo_info "Building backend image..."
gcloud builds submit ./backend \
    --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
    --timeout=20m

# Build and push frontend image
echo_info "Building frontend image..."
gcloud builds submit ./frontend \
    --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
    --timeout=20m

# Deploy backend with secrets
echo_info "Deploying backend service with Secret Manager integration..."
gcloud run deploy $BACKEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8000 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars ENVIRONMENT=production \
    --set-secrets="DATABASE_URL=database-url:latest,GCP_PROJECT_ID=gcp-project-id:latest"

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format 'value(status.url)')
echo_info "Backend deployed at: $BACKEND_URL"

# Deploy frontend with backend URL
echo_info "Deploying frontend service..."
gcloud run deploy $FRONTEND_SERVICE \
    --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 3000 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --platform managed --region $REGION --format 'value(status.url)')

echo_info "Deployment completed successfully!"
echo_info "Backend URL: $BACKEND_URL"
echo_info "Frontend URL: $FRONTEND_URL"

echo_warn "Remember to:"
echo_warn "1. Set up your PostgreSQL database on GCP Cloud SQL"
echo_warn "2. Update backend environment variables with database connection details"
echo_warn "3. Run database migrations"
echo_warn "4. Configure CORS settings if needed"