#!/bin/bash

# TMG Market Research - Database Setup Script for GCP Cloud SQL
# This script creates a Cloud SQL PostgreSQL instance and runs migrations

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
DB_INSTANCE_NAME="tmg-market-research-db"
DB_NAME="market_research"
DB_USER="app_user"
DB_PASSWORD=${3:-""}

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
    echo "Usage: ./setup-database.sh YOUR_PROJECT_ID [REGION] [DB_PASSWORD]"
    exit 1
fi

# Generate password if not provided
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32)
    echo_info "Generated database password: $DB_PASSWORD"
fi

echo_info "Setting up database for project: $PROJECT_ID"
echo_info "Region: $REGION"
echo_info "Instance: $DB_INSTANCE_NAME"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo_info "Enabling required APIs..."
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Check if instance already exists
if gcloud sql instances describe $DB_INSTANCE_NAME --quiet 2>/dev/null; then
    echo_info "Database instance $DB_INSTANCE_NAME already exists"
else
    # Create Cloud SQL instance
    echo_info "Creating Cloud SQL PostgreSQL instance..."
    gcloud sql instances create $DB_INSTANCE_NAME \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --authorized-networks=0.0.0.0/0 \
        --storage-type=SSD \
        --storage-size=10GB
fi

# Set root password
echo_info "Setting up database passwords..."
gcloud sql users set-password postgres \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD

# Create application user
echo_info "Creating application user..."
gcloud sql users create $DB_USER \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD

# Create database
echo_info "Creating database..."
gcloud sql databases create $DB_NAME \
    --instance=$DB_INSTANCE_NAME

# Get connection details
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)")
INSTANCE_IP=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(ipAddresses[0].ipAddress)")

# Store secrets in Secret Manager
echo_info "Storing credentials in Google Secret Manager..."
DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$INSTANCE_IP/$DB_NAME"

# Create or update secrets
echo -n "$DATABASE_URL" | gcloud secrets create database-url --data-file=- --quiet || \
echo -n "$DATABASE_URL" | gcloud secrets versions add database-url --data-file=- --quiet

echo -n "$DB_PASSWORD" | gcloud secrets create db-password --data-file=- --quiet || \
echo -n "$DB_PASSWORD" | gcloud secrets versions add db-password --data-file=- --quiet

echo -n "$INSTANCE_IP" | gcloud secrets create db-host --data-file=- --quiet || \
echo -n "$INSTANCE_IP" | gcloud secrets versions add db-host --data-file=- --quiet

echo -n "$DB_NAME" | gcloud secrets create db-name --data-file=- --quiet || \
echo -n "$DB_NAME" | gcloud secrets versions add db-name --data-file=- --quiet

echo -n "$DB_USER" | gcloud secrets create db-user --data-file=- --quiet || \
echo -n "$DB_USER" | gcloud secrets versions add db-user --data-file=- --quiet

echo -n "$PROJECT_ID" | gcloud secrets create gcp-project-id --data-file=- --quiet || \
echo -n "$PROJECT_ID" | gcloud secrets versions add gcp-project-id --data-file=- --quiet

echo_info "Database setup completed!"
echo_info "Connection name: $CONNECTION_NAME"
echo_info "Instance IP: $INSTANCE_IP"
echo_info "Database name: $DB_NAME"
echo_info "Username: $DB_USER"

echo_info "✅ Secrets stored in Secret Manager:"
echo "   🔐 database-url"
echo "   🔐 db-password"
echo "   🔐 db-host"
echo "   🔐 db-name"
echo "   🔐 db-user"
echo "   🔐 gcp-project-id"

echo_warn "Your backend will automatically use these secrets when deployed."
echo_warn "Manual environment variables (for reference only):"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$INSTANCE_IP/$DB_NAME"
echo "GCP_PROJECT_ID=$PROJECT_ID"