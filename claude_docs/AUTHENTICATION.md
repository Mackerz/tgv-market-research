# Authentication Setup Guide

This guide explains how to set up authentication for the Market Research application, including both username/password authentication for development and Google SSO for production.

## Overview

The application supports two authentication methods:

1. **Username/Password Authentication** - Enabled in development, available as backup in production
2. **Google SSO** - Primary method for production environments

## Backend Configuration

### Required Environment Variables

Add these variables to your backend `.env` file:

```bash
# Environment (development or production)
ENVIRONMENT=development

# JWT Secret Key (generate a secure random key for production)
SECRET_KEY=your-secret-key-here

# Google OAuth (required for production Google SSO)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# API Key (optional, for backward compatibility)
API_KEY=your-api-key-here
```

### Generating Secure Keys

#### Generate SECRET_KEY (Python)
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Generate API_KEY (Python)
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Google OAuth Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Sign-In API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sign-In API" and enable it

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Web application"
   - Add authorized JavaScript origins:
     - `http://localhost:3000` (for local development)
     - `https://your-production-domain.com` (for production)
   - Add authorized redirect URIs:
     - `http://localhost:3000/login` (for local development)
     - `https://your-production-domain.com/login` (for production)
   - Save the Client ID and Client Secret

4. **Configure Credentials**
   - Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to your backend `.env`
   - Add `NEXT_PUBLIC_GOOGLE_CLIENT_ID` to your frontend `.env.production`

## Frontend Configuration

### Development Environment (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

### Production Environment (.env.production)

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
NODE_ENV=production
```

## Database Setup

### Run Migration

The authentication system requires new database columns. Run the migration:

```bash
cd backend
poetry run alembic upgrade head
```

### Create Admin User

You'll need to create at least one admin user to access the reporting dashboard.

#### Option 1: Using Python Shell

```bash
cd backend
poetry shell
python
```

```python
from app.core.database import SessionLocal
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate

# Create database session
db = SessionLocal()

# Create admin user
user_data = UserCreate(
    username="admin",
    email="admin@example.com",
    full_name="Admin User",
    password="your-secure-password"
)

new_user = user_crud.create(db, obj_in=user_data)

# Set as admin
new_user.is_admin = True
db.commit()

print(f"Created admin user: {new_user.username}")
db.close()
```

#### Option 2: Using Database Direct SQL

```sql
-- First, create the user (replace with your values)
INSERT INTO users (username, email, full_name, hashed_password, is_active, is_admin)
VALUES (
    'admin',
    'admin@example.com',
    'Admin User',
    '$2b$12$your_hashed_password_here',  -- Generate using bcrypt
    true,
    true
);
```

To generate a bcrypt hash for a password:

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("your-password-here"))
```

## Authentication Behavior

### Development Mode (`ENVIRONMENT=development`)

- Username/password authentication is enabled
- Google SSO is disabled (even if credentials are configured)
- API key authentication is optional (bypassed if not set)
- Login page shows username/password form only

### Production Mode (`ENVIRONMENT=production`)

- Google SSO is the primary authentication method (if `GOOGLE_CLIENT_ID` is set)
- Username/password authentication is available as backup
- API key authentication is required for programmatic access
- Login page shows both Google SSO button and username/password form

## Testing Authentication

### Test Username/Password Login

1. Start the backend server:
   ```bash
   cd backend
   poetry run uvicorn app.main:app --reload
   ```

2. Start the frontend server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to `http://localhost:3000/login`

4. Enter your admin credentials and click "Sign in"

5. You should be redirected to `/report` if successful

### Test Google SSO (Production Only)

1. Set `ENVIRONMENT=production` in backend `.env`

2. Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set

3. Add `NEXT_PUBLIC_GOOGLE_CLIENT_ID` to frontend `.env.production`

4. Restart both servers

5. Navigate to the login page and click "Sign in with Google"

6. Complete the Google authentication flow

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/login` - Username/password login
- `POST /api/auth/google` - Google SSO login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user
- `GET /api/auth/check` - Check auth configuration

### Protected Endpoints

All report endpoints now require authentication:

- `GET /api/reports/{survey_slug}/submissions` - Get report submissions
- `GET /api/reports/{survey_slug}/submissions/{id}` - Get submission details
- `PUT /api/reports/{survey_slug}/submissions/{id}/approve` - Approve submission
- `PUT /api/reports/{survey_slug}/submissions/{id}/reject` - Reject submission
- `GET /api/reports/{survey_slug}/data` - Get reporting data
- `GET /api/reports/{survey_slug}/media-gallery` - Get media gallery
- `GET /api/reports/{survey_slug}/settings` - Get report settings
- `PUT /api/reports/{survey_slug}/settings/*` - Update report settings

## Troubleshooting

### "Not authenticated" Error

- Check that cookies are enabled in your browser
- Verify that `credentials: 'include'` is set in all frontend API calls
- Ensure the backend is returning the `Set-Cookie` header
- Check CORS configuration allows credentials

### Google SSO Not Working

- Verify `GOOGLE_CLIENT_ID` matches exactly (no extra spaces)
- Check that your domain is in the authorized origins list
- Ensure the Google Sign-In script is loading (check browser console)
- Verify `ENVIRONMENT=production` is set

### Migration Fails

- Ensure the database is running: `docker compose up -d db`
- Check the database connection string in `.env`
- Verify you're in the backend directory when running migrations

### Can't Access Reports

- Ensure your user has `is_admin=True` in the database
- Check that you're logged in (visit `/api/auth/me` to verify)
- Clear browser cookies and try logging in again

## Security Notes

1. **Always use HTTPS in production** - The `secure` flag on cookies requires HTTPS
2. **Keep SECRET_KEY secret** - Never commit it to version control
3. **Rotate keys regularly** - Change SECRET_KEY and API_KEY periodically
4. **Use strong passwords** - Enforce password requirements in production
5. **Enable 2FA for Google accounts** - All admin users should have 2FA enabled
6. **Review admin users regularly** - Remove inactive admin accounts

## Next Steps

After setting up authentication:

1. Create admin users for your team
2. Test the login flow in both development and production
3. Configure Google OAuth for production
4. Set up proper secrets management (e.g., GCP Secret Manager)
5. Enable HTTPS for production deployments
6. Configure proper CORS settings for your domains
