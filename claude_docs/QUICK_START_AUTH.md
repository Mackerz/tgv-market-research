# Authentication Quick Start

## 🚀 Get Started in 5 Minutes

### Step 1: Generate Secret Key

```bash
cd backend
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
echo "ENVIRONMENT=development" >> .env
```

### Step 2: Run Database Migration

```bash
# Make sure database is running
docker compose up -d db

# Run migration
poetry run alembic upgrade head
```

### Step 3: Create Admin User

```bash
# Interactive mode (recommended)
python create_admin.py

# Or with arguments
python create_admin.py --username admin --email admin@example.com --full-name "Admin User"
```

### Step 4: Start Servers

```bash
# Terminal 1 - Backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 5: Test Login

1. Open browser to `http://localhost:3000/report`
2. You'll be redirected to `/login`
3. Enter your admin credentials
4. You should see the report dashboard

## ✅ That's It!

You now have:
- ✅ Login page with username/password
- ✅ Protected report routes
- ✅ Session-based authentication
- ✅ Automatic redirects

## 🎯 Production Setup (Google SSO)

### Additional Steps for Production:

1. **Set Environment**
   ```bash
   echo "ENVIRONMENT=production" > backend/.env
   ```

2. **Get Google OAuth Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials
   - Add authorized origins and redirect URIs

3. **Configure Backend**
   ```bash
   echo "GOOGLE_CLIENT_ID=your-client-id" >> backend/.env
   echo "GOOGLE_CLIENT_SECRET=your-client-secret" >> backend/.env
   ```

4. **Configure Frontend**
   ```bash
   echo "NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id" >> frontend/.env.production
   ```

5. **Restart Servers**

Now your login page will show both Google SSO and username/password options!

## 📚 Need More Help?

- **Full Setup Guide**: See `AUTHENTICATION.md`
- **Implementation Details**: See `AUTH_SUMMARY.md`
- **Troubleshooting**: Check the troubleshooting section in `AUTHENTICATION.md`

## 🔑 Default Test Credentials

After running `create_admin.py`, use the credentials you created to log in.

**Security Note**: Change default passwords in production!

## 🛠️ Common Commands

### Create Another Admin User
```bash
cd backend
python create_admin.py
```

### Check if User is Admin
```bash
cd backend
poetry shell
python
```
```python
from app.core.database import SessionLocal
from app.crud.user import user as user_crud

db = SessionLocal()
user = user_crud.get_by_username(db, "admin")
print(f"Is admin: {user.is_admin}")
db.close()
```

### Make Existing User an Admin
```bash
cd backend
poetry shell
python
```
```python
from app.core.database import SessionLocal
from app.crud.user import user as user_crud

db = SessionLocal()
user = user_crud.get_by_username(db, "username")
user.is_admin = True
db.commit()
print("User is now an admin")
db.close()
```

### Reset Migration (if needed)
```bash
cd backend
poetry run alembic downgrade -1  # Go back one migration
poetry run alembic upgrade head   # Apply migration again
```

## 🔒 Security Checklist

- [ ] Changed default passwords
- [ ] Generated secure SECRET_KEY
- [ ] Set ENVIRONMENT correctly
- [ ] Enabled HTTPS in production
- [ ] Configured CORS properly
- [ ] Set httpOnly and secure flags on cookies
- [ ] Reviewed admin user list
- [ ] Tested login/logout flow

## 📞 Support

If you encounter issues:

1. Check the console for error messages
2. Verify environment variables are set correctly
3. Ensure database migration completed successfully
4. Check that user has `is_admin=True` in database
5. Try clearing browser cookies
6. Consult `AUTHENTICATION.md` for detailed troubleshooting
