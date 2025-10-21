from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv
from app.integrations.gcp.secrets import get_database_url

load_dotenv()

logger = logging.getLogger(__name__)

try:
    DATABASE_URL = get_database_url()
    logger.info("✅ Database URL retrieved successfully")
except Exception as e:
    logger.error(f"❌ Failed to get database URL: {e}")
    # Fallback for local development
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/fastapi_db")
    logger.warning(f"⚠️ Using fallback database URL")

# Configure connection pooling for production
# pool_size: number of connections to keep open
# max_overflow: additional connections that can be created beyond pool_size
# pool_recycle: recycle connections after 1 hour to prevent stale connections
# pool_pre_ping: verify connections are alive before using them

# Only apply pooling parameters for PostgreSQL (not SQLite in tests)
if DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't support pool_size/max_overflow parameters
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    logger.info("🔧 Database engine configured for SQLite (testing mode)")
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,              # Keep 10 connections in pool
        max_overflow=20,           # Allow up to 30 total connections (10 + 20)
        pool_recycle=3600,         # Recycle connections after 1 hour
        pool_pre_ping=True,        # Test connection health before use
        echo=False,                # Set to True for SQL debugging
    )
    logger.info(f"🔧 Database engine configured with connection pooling:")
    logger.info(f"   - Pool size: 10, Max overflow: 20")
    logger.info(f"   - Pool recycle: 3600s, Pre-ping: enabled")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()