from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv
from secrets_manager import get_database_url

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

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()