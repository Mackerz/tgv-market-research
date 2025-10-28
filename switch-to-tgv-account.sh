#!/bin/bash

# Quick script to switch to ThatGlobalView Google account
# Run this before deploying to TGV projects

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo "=========================================="
echo "Switching to ThatGlobalView Account"
echo "=========================================="
echo ""

# Check current account
CURRENT_ACCOUNT=$(gcloud config get-value account 2>/dev/null || echo "none")
print_info "Current account: $CURRENT_ACCOUNT"

# Check if TGV configuration exists
if gcloud config configurations describe tgv &>/dev/null; then
    print_info "TGV configuration found, activating..."
    gcloud config configurations activate tgv
else
    print_warn "TGV configuration not found, creating..."

    # Create new configuration
    gcloud config configurations create tgv

    # Set account
    gcloud config set account mackers@thatglobalview.com

    # Login
    print_info "Authenticating with mackers@thatglobalview.com..."
    gcloud auth login mackers@thatglobalview.com

    # List projects and prompt for selection
    echo ""
    print_info "Available projects:"
    gcloud projects list
    echo ""
    read -p "Enter your TGV project ID: " TGV_PROJECT
    gcloud config set project $TGV_PROJECT
fi

# Verify
echo ""
echo "=========================================="
print_info "Configuration Active"
echo "=========================================="
echo ""
gcloud config list
echo ""

# Show quick commands
echo "📋 Quick Commands:"
echo "  View services:  gcloud run services list --region us-central1"
echo "  Deploy:         gcloud builds submit --config=cloudbuild.yaml ."
echo "  View logs:      gcloud run services logs read tmg-market-research-backend --region us-central1"
echo ""
echo "🔄 To switch back to personal account:"
echo "  gcloud config configurations activate personal"
echo ""
echo "  (If personal config doesn't exist, create it first:)"
echo "  gcloud config configurations create personal"
echo "  gcloud config set account mackersmcvey@gmail.com"
echo ""
