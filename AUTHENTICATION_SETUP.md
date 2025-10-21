# Authentication Setup Guide

## Overview

The API uses **API key-based authentication** to protect admin endpoints. Survey response endpoints remain public for easy user access.

---

## Protected Endpoints (Require API Key)

**Survey Management:**
- `POST /api/surveys/` - Create survey
- `PUT /api/surveys/{id}` - Update survey
- `DELETE /api/surveys/{id}` - Delete survey

**Submission Management:**
- `PUT /api/reports/{slug}/submissions/{id}/approve` - Approve submission
- `PUT /api/reports/{slug}/submissions/{id}/reject` - Reject submission

**AI Analysis:**
- `POST /api/responses/{id}/trigger-analysis` - Trigger manual AI analysis

---

## Public Endpoints (No Authentication)

**Survey Responses:**
- `GET /api/surveys/` - List surveys
- `GET /api/surveys/{slug}` - Get survey details
- `POST /api/surveys/{slug}/submit` - Create submission
- `POST /api/submissions/{id}/responses` - Create response
- `POST /api/surveys/{slug}/upload/photo` - Upload photo
- `POST /api/surveys/{slug}/upload/video` - Upload video
- `PUT /api/submissions/{id}/complete` - Mark submission complete

**Reporting (Read-only):**
- `GET /api/reports/{slug}/submissions` - Get submissions
- `GET /api/reports/{slug}/data` - Get report data
- `GET /api/reports/{slug}/media-gallery` - Get media gallery

---

## Setup Instructions

### Step 1: Generate an API Key

Run this Python script to generate a secure API key:

```python
import secrets
api_key = secrets.token_hex(32)
print(f"Your API Key: {api_key}")
```

Or use the built-in generator:

```python
from app.core.auth import generate_api_key
print(generate_api_key())
```

Example output:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### Step 2: Store the API Key

**For Development (Local):**

Add to your `.env` file:
```bash
API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**For Production (GCP):**

Store in Secret Manager:
```bash
# Create the secret
echo -n "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2" | \
  gcloud secrets create api-key \
    --data-file=- \
    --replication-policy="automatic"

# Grant access to your service account
gcloud secrets add-iam-policy-binding api-key \
    --member="serviceAccount:YOUR-SERVICE-ACCOUNT@PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Step 3: Restart the Application

The API key will be loaded on startup:
```bash
# Development
docker-compose restart backend

# Production (Cloud Run will auto-restart)
gcloud run services update backend-service --region=us-central1
```

---

## Using the API Key

### cURL Example

```bash
# Without API Key (Public endpoint - works)
curl -X GET http://localhost:8000/api/surveys/

# With API Key (Admin endpoint - required)
curl -X POST http://localhost:8000/api/surveys/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "name": "Customer Feedback Survey",
    "survey_slug": "customer-feedback",
    "client": "Acme Corp"
  }'
```

### Python Example

```python
import requests

API_KEY = "your-api-key-here"
BASE_URL = "http://localhost:8000"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Create a survey (requires auth)
response = requests.post(
    f"{BASE_URL}/api/surveys/",
    headers=headers,
    json={
        "name": "Customer Feedback Survey",
        "survey_slug": "customer-feedback",
        "client": "Acme Corp"
    }
)

print(response.json())
```

### JavaScript/TypeScript Example

```typescript
const API_KEY = 'your-api-key-here';
const BASE_URL = 'http://localhost:8000';

// Create a survey (requires auth)
const response = await fetch(`${BASE_URL}/api/surveys/`, {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'Customer Feedback Survey',
    survey_slug: 'customer-feedback',
    client: 'Acme Corp',
  }),
});

const data = await response.json();
console.log(data);
```

---

## Error Responses

### 401 Unauthorized (Missing API Key)

```json
{
  "detail": "API key required. Provide via X-API-Key header."
}
```

**Solution:** Add the `X-API-Key` header to your request.

### 403 Forbidden (Invalid API Key)

```json
{
  "detail": "Invalid API key"
}
```

**Solution:** Check that you're using the correct API key.

---

## Development Mode

If no API key is configured, the application runs in **development mode** with authentication disabled. You'll see this warning in the logs:

```
⚠️ No API key configured - authentication disabled (dev mode only!)
```

**WARNING:** Never deploy to production without configuring an API key!

---

## Security Best Practices

1. **Never commit API keys to version control**
   - Use `.env` files (already in `.gitignore`)
   - Use GCP Secret Manager for production

2. **Rotate keys periodically**
   - Generate new keys every 90 days
   - Update in Secret Manager
   - Notify API consumers

3. **Use different keys per environment**
   - Development: `API_KEY_DEV`
   - Staging: `API_KEY_STAGING`
   - Production: `API_KEY_PROD`

4. **Monitor API key usage**
   - Check Cloud Logging for auth failures
   - Alert on unusual patterns
   - Revoke compromised keys immediately

5. **Use HTTPS in production**
   - Cloud Run provides automatic HTTPS
   - Never send API keys over HTTP

---

## Troubleshooting

### Problem: "API key required" but I sent the header

**Check:**
1. Header name is `X-API-Key` (case-sensitive)
2. No extra spaces in the key value
3. Key matches what's in `.env` or Secret Manager

### Problem: Authentication works locally but not in production

**Check:**
1. API key is stored in GCP Secret Manager as `api-key`
2. Service account has `secretmanager.secretAccessor` role
3. Cloud Run service is using correct service account
4. Restart the Cloud Run service after creating the secret

### Problem: Want to disable authentication temporarily

**For development only:**
```bash
# Remove or comment out the API_KEY in .env
# API_KEY=...

# Restart the backend
docker-compose restart backend
```

---

## API Documentation

View the interactive API documentation with authentication examples:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

In Swagger UI, click the "Authorize" button and enter your API key to test protected endpoints.

---

## Next Steps

After setting up authentication:

1. Generate and store your API key
2. Test with a protected endpoint (e.g., create survey)
3. Update your frontend/client applications with the API key
4. Set up key rotation schedule
5. Monitor auth logs for suspicious activity

---

**Generated:** 2025-10-21
**File Location:** `/home/mackers/tmg/marketResearch/AUTHENTICATION_SETUP.md`
