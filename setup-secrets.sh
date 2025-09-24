#!/bin/bash

# TMG Market Research - Additional Secrets Setup Script
# This script helps you set up additional secrets in Google Secret Manager

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}

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

# Check if project ID is provided
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo_error "Please provide your GCP project ID as the first argument"
    echo "Usage: ./setup-secrets.sh YOUR_PROJECT_ID"
    exit 1
fi

echo_info "Setting up additional secrets for project: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

# Enable Secret Manager API
echo_info "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

echo_info "Setting up additional application secrets..."

# Gemini API Key
echo_warn "Enter your Gemini API Key (press Enter to skip):"
read -s GEMINI_API_KEY
if [ ! -z "$GEMINI_API_KEY" ]; then
    echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- --quiet || \
    echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=- --quiet
    echo_info "✅ Gemini API key stored"
else
    echo_warn "⚠️ Skipping Gemini API key"
fi

# GCS Bucket Name
echo_warn "Enter your GCS Bucket Name for media storage (press Enter to skip):"
read GCS_BUCKET_NAME
if [ ! -z "$GCS_BUCKET_NAME" ]; then
    echo -n "$GCS_BUCKET_NAME" | gcloud secrets create gcs-bucket-name --data-file=- --quiet || \
    echo -n "$GCS_BUCKET_NAME" | gcloud secrets versions add gcs-bucket-name --data-file=- --quiet
    echo_info "✅ GCS bucket name stored"
else
    echo_warn "⚠️ Skipping GCS bucket name"
fi

# CORS Origins
echo_warn "Enter allowed CORS origins (comma-separated, press Enter for default: http://localhost:3000):"
read CORS_ORIGINS
CORS_ORIGINS=${CORS_ORIGINS:-"http://localhost:3000"}
echo -n "$CORS_ORIGINS" | gcloud secrets create allowed-origins --data-file=- --quiet || \
echo -n "$CORS_ORIGINS" | gcloud secrets versions add allowed-origins --data-file=- --quiet
echo_info "✅ CORS origins stored: $CORS_ORIGINS"

echo_info "All secrets have been set up!"

echo_warn "To update your deployment with these new secrets, run:"
echo "gcloud run services update tmg-market-research-backend \\"
echo "  --region=us-central1 \\"
echo "  --set-secrets=\"GEMINI_API_KEY=gemini-api-key:latest,GCS_BUCKET_NAME=gcs-bucket-name:latest,ALLOWED_ORIGINS=allowed-origins:latest\""

echo_warn "Existing secrets in Secret Manager:"
gcloud secrets list --filter="name:database-url OR name:db-password OR name:gcp-project-id OR name:gemini-api-key OR name:gcs-bucket-name OR name:allowed-origins" --format="table(name)" | grep -v NAME || echo "No secrets found"