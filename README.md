# Full Stack Application

A modern full-stack web application built with NextJS frontend, FastAPI backend, and PostgreSQL database, all containerized with Docker.

## How It Works

This project demonstrates a complete full-stack architecture:

1. **Frontend (NextJS)**: React-based frontend with server-side rendering, TypeScript support, and Tailwind CSS for styling
2. **Backend (FastAPI)**: High-performance Python API with automatic documentation and type validation
3. **Database (PostgreSQL)**: Robust relational database for data persistence
4. **Containerization**: Each service runs in its own Docker container for consistent deployment

### Architecture Flow

```
Browser → NextJS Frontend → FastAPI Backend → PostgreSQL Database
  :3000        :3000           :8000            :5432
```

The frontend makes HTTP requests to the backend API, which processes the requests and interacts with the PostgreSQL database as needed.

## Project Structure

```
.
├── frontend/                    # NextJS application with Tailwind CSS
│   ├── src/app/                # App router directory
│   │   └── page.tsx           # Home page with API connection demo
│   ├── Dockerfile             # Frontend container configuration
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.ts     # Tailwind CSS configuration
├── backend/                     # FastAPI application
│   ├── main.py                # FastAPI app with routes and CORS
│   ├── database.py            # SQLAlchemy database configuration
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend container configuration
│   └── .env                  # Environment variables
├── docker-compose.yml          # Multi-container orchestration
└── README.md                   # This file
```

## Key Files Explained

### Frontend (`frontend/src/app/page.tsx`)
- React component that demonstrates API connectivity
- Shows real-time connection status to the backend
- Uses Tailwind CSS for styling
- Implements client-side data fetching

### Backend (`backend/main.py`)
- FastAPI application with CORS enabled for frontend communication
- Database integration using SQLAlchemy
- Health check endpoint that verifies database connectivity
- Automatic API documentation at `/docs`

### Database Configuration (`backend/database.py`)
- SQLAlchemy setup for PostgreSQL connection
- Database session management
- Base model class for future database models

### Docker Setup (`docker-compose.yml`)
- Orchestrates three services: frontend, backend, and database
- Handles service dependencies and networking
- Persistent data storage for PostgreSQL

## Quick Start with Docker

1. **Build and run all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the applications:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Setup

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (NextJS)
```bash
cd frontend
npm install
npm run dev
```

### Database (PostgreSQL)
The database runs in Docker. Connection details are in `backend/.env`.

## Environment Variables

Backend environment variables are in `backend/.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

## API Endpoints

### Basic Endpoints
- `GET /` - Hello World
- `GET /hello/{name}` - Personalized greeting
- `GET /api/health` - Health check with database status

### User Management (ORM)
- `POST /api/users/` - Create new user
- `GET /api/users/` - List all users
- `GET /api/users/{user_id}` - Get user with posts
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

### Post Management (ORM)
- `POST /api/users/{user_id}/posts/` - Create post for user
- `GET /api/posts/` - List all posts with authors
- `GET /api/posts/{post_id}` - Get specific post
- `PUT /api/posts/{post_id}` - Update post
- `DELETE /api/posts/{post_id}` - Delete post

## Database Models (SQLAlchemy ORM)

### User Model
- `id`: Primary key
- `email`: Unique email address (with validation)
- `username`: Unique username
- `full_name`: Optional full name
- `is_active`: Boolean status
- `created_at/updated_at`: Timestamps

### Post Model
- `id`: Primary key
- `title`: Post title
- `content`: Optional post content
- `published`: Boolean publication status
- `author_id`: Foreign key to User
- `created_at/updated_at`: Timestamps

### Database Migrations
The project uses Alembic for database migrations:
- Initial migration creates User and Post tables
- Migration files in `backend/alembic/versions/`
- Run migrations: `cd backend && alembic upgrade head`

## How to Use This Project

### 1. Development Workflow
1. Start the services: `docker-compose up --build`
2. Make changes to your code
3. Frontend changes auto-reload at http://localhost:3000
4. Backend changes require container restart (or use volume mounting for hot reload)

### 2. Adding New Features
- **Frontend**: Add new React components in `frontend/src/`
- **Backend**: Add new API endpoints in `backend/main.py` or create new modules
- **Database**: Create models in `backend/` and use Alembic for migrations

### 3. API Testing
- Use the interactive docs at http://localhost:8000/docs
- Test with the included `test_main.http` file
- Frontend automatically tests `/api/health` endpoint

## Technologies

- **Frontend**: NextJS 14, React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Python 3.11
- **Database**: PostgreSQL 15
- **Deployment**: Docker & Docker Compose

## What You Get

✅ Modern React frontend with TypeScript and Tailwind CSS
✅ High-performance Python API with automatic documentation
✅ **SQLAlchemy ORM with PostgreSQL** - Complete database modeling
✅ **Database migrations with Alembic** - Version control for database schema
✅ **Full CRUD operations** - Create, Read, Update, Delete for all models
✅ **Pydantic schemas** - Type validation and serialization
✅ **Relationship mapping** - User-Post foreign key relationships
✅ **Interactive demo interface** - Create users and posts through the web UI
✅ Docker containerization for consistent deployment
✅ CORS configuration for frontend-backend communication
✅ Development-ready setup with hot reloading
✅ Production-ready Docker configuration

## ORM Demo Features

The frontend includes a complete ORM demonstration:
- **Create Users**: Add new users with email validation
- **Create Posts**: Write posts and assign them to users
- **View Relationships**: See posts with their authors
- **Real-time Updates**: Changes reflect immediately in the UI
- **Type Safety**: Full TypeScript integration