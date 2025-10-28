# Deploying to a Different Google Account

## Overview
This guide covers deploying the TMG Market Research application to a GCP project under a **different Google account** (`mackers@thatglobalview.com` instead of `mackersmcvey@gmail.com`).

## Important: Account Management

Since you're deploying to a different account, you'll need to:
1. Switch your active gcloud account
2. Ensure you have proper permissions in the target account
3. Configure GitHub Actions/Cloud Build with the correct service account

---

## Step 1: Switch Google Cloud Account

### A. List Current Accounts

```bash
# See all authenticated accounts
gcloud auth list

# Check current active account
gcloud config get-value account
```

### B. Authenticate with New Account

```bash
# Login with the ThatGlobalView account
gcloud auth login mackers@thatglobalview.com

# This will open a browser window for authentication
# Follow the prompts to authenticate
```

### C. Set as Active Account

```bash
# Set the ThatGlobalView account as active
gcloud config set account mackers@thatglobalview.com

# Verify it's set
gcloud auth list
# Should show mackers@thatglobalview.com with an asterisk (*)
```

### D. Revoke Old Account Access (Optional)

```bash
# If you want to temporarily revoke the old account to avoid confusion
gcloud auth revoke mackersmcvey@gmail.com

# You can always re-authenticate later
# gcloud auth login mackersmcvey@gmail.com
```

---

## Step 2: List and Select Target Project

### A. List Available Projects

```bash
# List all projects you have access to with the new account
gcloud projects list

# Example output:
# PROJECT_ID              NAME                PROJECT_NUMBER
# tgv-market-research     TGV Market Research 123456789012
```

### B. Set Active Project

```bash
# Set your target project
gcloud config set project YOUR-TGV-PROJECT-ID

# Verify
gcloud config get-value project
```

---

## Step 3: Run Automated Setup

Now that you're authenticated with the correct account, run the setup script:

```bash
./setup-new-gcp-project.sh
```

**The script will:**
- Use your currently active account (`mackers@thatglobalview.com`)
- Create infrastructure in the project you specified
- Configure all necessary permissions

---

## Step 4: Configure GitHub Repository Access

Since the repository is under the `Mackerz` GitHub account, you need to grant the new GCP project access:

### A. Grant Cloud Build Access to GitHub

1. Go to [Cloud Build GitHub App](https://github.com/apps/google-cloud-build)
2. Click "Configure"
3. Select your account (`Mackerz`)
4. Under "Repository access", ensure `tgv-market-research` is selected
5. Save

### B. Connect Repository in GCP Console

```bash
# Set your TGV project
gcloud config set project YOUR-TGV-PROJECT-ID

# Open Cloud Build in browser
echo "Go to: https://console.cloud.google.com/cloud-build/triggers?project=$(gcloud config get-value project)"
```

Then:
1. Click "Connect Repository"
2. Select "GitHub (Cloud Build GitHub App)"
3. Authenticate (you may need to authenticate with your Mackerz GitHub account)
4. Select repository: `Mackerz/tgv-market-research`
5. Create a trigger:
   - **Name:** `deploy-main`
   - **Event:** Push to branch
   - **Branch:** `^main$`
   - **Configuration:** `cloudbuild.yaml`
   - **Service account:** Leave as default (or use your custom service account)

---

## Step 5: Configure Service Account Permissions

The Cloud Build service account needs permissions:

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant Cloud Build service account necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Step 6: Configure Google OAuth

**Important:** Since this is a different account, you need to create **new** OAuth credentials:

### A. Create OAuth 2.0 Credentials

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
   - Make sure you're in the **TGV project** (check project selector at top)
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Application type: **Web application**
4. Name: `TMG Market Research`
5. Authorized JavaScript origins:
   ```
   http://localhost:3000
   https://your-frontend-url.run.app
   ```
6. Authorized redirect URIs:
   ```
   http://localhost:3000
   https://your-frontend-url.run.app
   ```
7. Click "Create"
8. **Save the Client ID and Client Secret**

### B. Add OAuth Secrets

```bash
# Add Google OAuth credentials to Secret Manager
echo -n "YOUR_NEW_CLIENT_ID.apps.googleusercontent.com" | \
  gcloud secrets create google-client-id --data-file=-

echo -n "YOUR_NEW_CLIENT_SECRET" | \
  gcloud secrets create google-client-secret --data-file=-
```

### C. Configure OAuth Consent Screen

1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select **External** (or Internal if using Google Workspace)
3. Fill in app information:
   - App name: `TMG Market Research`
   - User support email: `mackers@thatglobalview.com`
   - Developer contact: `mackers@thatglobalview.com`
4. Add scopes:
   - `email`
   - `profile`
   - `openid`
5. Add test users if in testing mode:
   - `mackers@thatglobalview.com`
   - Any other test users

---

## Step 7: Update Configuration Files

### A. Update `cloudbuild.yaml` Secrets

The main `cloudbuild.yaml` already references secrets, but verify line 51 includes all needed secrets:

```yaml
--set-secrets=DATABASE_URL=database-url:latest,
  GCP_PROJECT_ID=gcp-project-id:latest,
  SECRET_KEY=secret-key:latest,
  API_KEY=api-key:latest,
  GOOGLE_CLIENT_ID=google-client-id:latest,
  GOOGLE_CLIENT_SECRET=google-client-secret:latest,
  GEMINI_API_KEY=gemini-api-key:latest,
  ALLOWED_ORIGINS=allowed-origins:latest,
  GCS_BUCKET_NAME=gcs-bucket-name:latest,
  GCP_STORAGE_BUCKET_PHOTOS=gcp-storage-bucket-photos:latest,
  GCP_STORAGE_BUCKET_VIDEOS=gcp-storage-bucket-videos:latest,
  GCP_STORAGE_BUCKET_QUESTION_MEDIA=gcp-storage-bucket-question-media:latest,
  GCP_STORAGE_ENABLED=gcp-storage-enabled:latest,
  GCP_AI_ENABLED=gcp-ai-enabled:latest
```

### B. Configure CORS Origins

After your first deploy, you'll get Cloud Run URLs. Add them to the allowed origins:

```bash
# Get your frontend URL
FRONTEND_URL=$(gcloud run services describe tmg-market-research-frontend \
  --platform managed --region us-central1 --format 'value(status.url)')

# Update CORS origins secret
echo -n "$FRONTEND_URL,http://localhost:3000" | \
  gcloud secrets versions add allowed-origins --data-file=-
```

---

## Step 8: Deploy Application

### A. Manual First Deploy

```bash
# Ensure you're in the correct project and account
gcloud config get-value account  # Should show mackers@thatglobalview.com
gcloud config get-value project  # Should show your TGV project

# Submit build
gcloud builds submit --config=cloudbuild.yaml .
```

### B. Monitor Deployment

```bash
# Watch build progress
gcloud builds log --stream $(gcloud builds list --limit=1 --format='value(id)')

# Once complete, get service URLs
gcloud run services list --platform managed --region us-central1
```

### C. Update Frontend with Backend URL

After backend deploys, get its URL and update `cloudbuild.yaml`:

```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe tmg-market-research-backend \
  --platform managed --region us-central1 --format 'value(status.url)')

echo "Backend URL: $BACKEND_URL"
```

Update `cloudbuild.yaml` line 69:
```yaml
- '--set-env-vars=NEXT_PUBLIC_API_URL=YOUR_BACKEND_URL'
```

Then redeploy:
```bash
git add cloudbuild.yaml
git commit -m "Update backend URL for TGV deployment"
git push origin main
```

---

## Step 9: Managing Multiple Accounts

### A. Create Named Configurations

For easier switching between accounts:

```bash
# Create configuration for ThatGlobalView account
gcloud config configurations create tgv
gcloud config set account mackers@thatglobalview.com
gcloud config set project YOUR-TGV-PROJECT-ID

# Create configuration for personal account
gcloud config configurations create personal
gcloud config set account mackersmcvey@gmail.com
gcloud config set project tmg-market-research

# Switch between configurations
gcloud config configurations activate tgv      # Switch to TGV
gcloud config configurations activate personal # Switch to personal

# List all configurations
gcloud config configurations list
```

### B. Using Multiple Accounts in Same Session

```bash
# Execute command with specific account
gcloud --account=mackers@thatglobalview.com projects list

# Or temporarily set account
export CLOUDSDK_CORE_ACCOUNT=mackers@thatglobalview.com
gcloud projects list
```

---

## Step 10: Verify Deployment

### A. Test Backend Health

```bash
BACKEND_URL=$(gcloud run services describe tmg-market-research-backend \
  --platform managed --region us-central1 --format 'value(status.url)')

curl $BACKEND_URL/api/health
# Should return: {"status":"healthy","database":"connected"}
```

### B. Test Frontend

```bash
FRONTEND_URL=$(gcloud run services describe tmg-market-research-frontend \
  --platform managed --region us-central1 --format 'value(status.url)')

echo "Visit: $FRONTEND_URL"
```

### C. Test Google SSO

1. Visit the frontend URL
2. Click "Sign in with Google"
3. Should see OAuth consent screen for TGV project
4. Sign in with any allowed email (test users or any if published)

---

## Common Issues & Solutions

### Issue 1: "Permission Denied" during deployment

**Solution:** Ensure you're authenticated with the correct account:
```bash
gcloud config get-value account
# Should show: mackers@thatglobalview.com
```

### Issue 2: OAuth callback fails

**Solution:** Update OAuth redirect URIs:
1. Get your actual Cloud Run frontend URL
2. Add it to Authorized redirect URIs in Google Console
3. Format: `https://your-actual-url.run.app`

### Issue 3: Database connection fails

**Solution:** Verify Cloud SQL connection string in secrets:
```bash
gcloud secrets versions access latest --secret=database-url
# Should show: postgresql://postgres:PASSWORD@/market_research?host=/cloudsql/PROJECT:REGION:INSTANCE
```

### Issue 4: Storage bucket access denied

**Solution:** Verify Cloud Run service account has storage permissions:
```bash
# Get service account
SA=$(gcloud run services describe tmg-market-research-backend \
  --platform managed --region us-central1 \
  --format='value(spec.template.spec.serviceAccountName)')

# Grant storage permissions
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:$SA" \
  --role="roles/storage.objectAdmin"
```

---

## Security Considerations

### Account Isolation

Since this is a separate business account:

1. **Keep accounts separate:** Don't grant `mackersmcvey@gmail.com` access to TGV project
2. **Use organization policies:** If using Google Workspace, apply org policies
3. **Audit access regularly:** Review IAM permissions monthly

### Service Account Best Practices

```bash
# Create dedicated service account for Cloud Run
gcloud iam service-accounts create tmg-market-research-prod \
  --display-name="TMG Market Research Production"

# Use it in Cloud Run deployment (update cloudbuild.yaml)
--service-account=tmg-market-research-prod@PROJECT_ID.iam.gserviceaccount.com
```

### Separate Environments

Consider creating multiple projects:
- `tgv-market-research-dev` - Development
- `tgv-market-research-staging` - Staging
- `tgv-market-research-prod` - Production

---

## Billing & Cost Management

Since this is a different billing account:

1. **Set up billing alerts:**
   ```bash
   # Go to: https://console.cloud.google.com/billing/budgets
   # Create budget alerts at $20, $50, $100
   ```

2. **Monitor costs:**
   ```bash
   # View current month costs
   gcloud billing accounts list
   ```

3. **Set quotas:**
   - Cloud Run: Max instances
   - Cloud SQL: Connection limits
   - Storage: Lifecycle policies

---

## Next Steps

1. ✅ Set up monitoring and alerting
2. ✅ Configure custom domain (optional)
3. ✅ Set up staging environment
4. ✅ Configure backup strategy
5. ✅ Document runbooks for TGV team

---

## Quick Reference

### Essential Commands

```bash
# Switch to TGV account
gcloud config configurations activate tgv

# Deploy
gcloud builds submit --config=cloudbuild.yaml .

# View logs
gcloud run services logs read tmg-market-research-backend --region us-central1

# Get URLs
gcloud run services list --platform managed --region us-central1

# Update secret
echo -n "new-value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

### Important URLs

- **GCP Console:** https://console.cloud.google.com
- **Cloud Build:** https://console.cloud.google.com/cloud-build
- **Cloud Run:** https://console.cloud.google.com/run
- **Secret Manager:** https://console.cloud.google.com/security/secret-manager
- **OAuth Credentials:** https://console.cloud.google.com/apis/credentials

---

## Support

For ThatGlobalView deployment issues:
- Contact: mackers@thatglobalview.com
- Project: [Your TGV Project ID]
- Account: mackers@thatglobalview.com
