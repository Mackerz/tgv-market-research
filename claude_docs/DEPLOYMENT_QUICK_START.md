# Quick Start: Deploy to ThatGlobalView Account

## TL;DR - Super Quick Deployment

```bash
# 1. Switch to TGV account
./switch-to-tgv-account.sh

# 2. Run automated setup (creates all infrastructure)
./setup-new-gcp-project.sh

# 3. Add Google OAuth credentials (one-time)
# Visit: https://console.cloud.google.com/apis/credentials
# Create OAuth 2.0 credentials, then:
gcloud secrets create google-client-id --data-file=<(echo -n "YOUR_CLIENT_ID")
gcloud secrets create google-client-secret --data-file=<(echo -n "YOUR_SECRET")

# 4. Deploy!
gcloud builds submit --config=cloudbuild.yaml .

# 5. Get your URLs
gcloud run services list --region us-central1
```

Done! Your app is live on Cloud Run.

---

## What You Need to Know

### Different Account = Different OAuth

Since you're deploying to `mackers@thatglobalview.com` (not `mackersmcvey@gmail.com`):

1. **New OAuth Credentials Required**
   - Must create OAuth credentials in the TGV project
   - Cannot reuse credentials from personal project
   - Configure consent screen for TGV

2. **Account Switching**
   - Use `./switch-to-tgv-account.sh` before deployment
   - Or manually: `gcloud config configurations activate tgv`

3. **Separate Infrastructure**
   - New Cloud SQL database
   - New Storage buckets
   - New Secret Manager secrets
   - Independent from personal project

---

## Common Questions

### Q: Do I need to change any code?
**A:** No! The code is environment-agnostic. All configuration is in Secret Manager.

### Q: Can I test locally before deploying?
**A:** Yes! Use Docker Compose:
```bash
docker compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Q: How do I manage two deployments (personal + TGV)?
**A:** Use gcloud configurations:
```bash
# TGV project
gcloud config configurations activate tgv
gcloud builds submit --config=cloudbuild.yaml .

# Personal project
gcloud config configurations activate personal
gcloud builds submit --config=cloudbuild.yaml .
```

### Q: What about costs?
**A:** ~$20-30/month for low traffic:
- Cloud Run: $10-20/month
- Cloud SQL (f1-micro): $9/month
- Storage: $0.50/month
- Auto-scales to zero when not in use

### Q: Can I use a custom domain?
**A:** Yes!
```bash
gcloud run domain-mappings create \
  --service tmg-market-research-frontend \
  --domain yourdomain.com \
  --region us-central1
```

---

## Directory of Documentation

- **`DEPLOYMENT_DIFFERENT_ACCOUNT.md`** - Full guide for deploying to different account (detailed)
- **`DEPLOYMENT_NEW_PROJECT.md`** - Complete infrastructure setup guide (step-by-step)
- **`DEPLOYMENT_QUICK_START.md`** - This file (quick reference)

---

## Support Scripts

- **`switch-to-tgv-account.sh`** - Switch gcloud to TGV account
- **`setup-new-gcp-project.sh`** - Automated infrastructure setup

---

## After Deployment Checklist

- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] Google SSO login works
- [ ] File upload works (test with survey creation)
- [ ] Database migrations ran successfully
- [ ] CORS configured correctly
- [ ] Monitoring/alerts set up
- [ ] Billing alerts configured
- [ ] Custom domain mapped (optional)
- [ ] Backup strategy documented

---

## Emergency Commands

```bash
# View live logs
gcloud run services logs tail tmg-market-research-backend --region us-central1

# Rollback deployment
gcloud run services update tmg-market-research-backend \
  --image gcr.io/PROJECT_ID/tmg-market-research-backend:PREVIOUS_SHA \
  --region us-central1

# Check service status
gcloud run services describe tmg-market-research-backend \
  --region us-central1 \
  --format='value(status.conditions[0].message)'

# Update secret
echo -n "new-value" | gcloud secrets versions add SECRET_NAME --data-file=-

# Scale down (if costs spike)
gcloud run services update tmg-market-research-backend \
  --max-instances=2 \
  --region us-central1
```

---

## Estimated Setup Time

- **Account switching:** 2 minutes
- **Automated setup:** 15-20 minutes (mostly Cloud SQL creation)
- **OAuth configuration:** 5 minutes
- **First deployment:** 10 minutes
- **Testing:** 10 minutes

**Total:** ~45 minutes to fully operational deployment

---

## Next Steps After Deployment

1. **Configure monitoring:** Set up Cloud Monitoring dashboards
2. **Set up alerts:** Budget alerts, error rate alerts, uptime checks
3. **Enable Cloud CDN:** For faster frontend delivery
4. **Set up staging:** Create separate staging project
5. **Document ops:** Create runbooks for your team
6. **Backup strategy:** Configure Cloud SQL backups

---

## Getting Help

If you run into issues:

1. Check logs: `gcloud run services logs read SERVICE_NAME --region us-central1`
2. Review secrets: `gcloud secrets list`
3. Verify IAM: `gcloud projects get-iam-policy PROJECT_ID`
4. Check quotas: `gcloud compute project-info describe --project PROJECT_ID`

Most issues are related to:
- OAuth misconfiguration
- Secret Manager access
- Service account permissions
- CORS settings

See `DEPLOYMENT_DIFFERENT_ACCOUNT.md` for detailed troubleshooting.
