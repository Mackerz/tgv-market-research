#!/usr/bin/env python3
"""
Script to create a user in the TMG Market Research database.
"""
import os
import sys
import bcrypt
import psycopg2
from datetime import datetime

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def create_user(username: str, email: str, password: str, full_name: str = None):
    """Create a user in the database."""

    # Get database connection string from environment or use default
    db_url = os.getenv("DATABASE_URL",
                       "postgresql://postgres:5tarTr3k@/market_research?host=/cloudsql/tgv-production:europe-west2:tgv-market-research-db")

    # Parse the connection string
    # Format: postgresql://user:password@/database?host=/cloudsql/instance
    if "host=/cloudsql/" in db_url:
        # Cloud SQL socket connection
        parts = db_url.split("@")
        user_pass = parts[0].replace("postgresql://", "")
        username_db, password_db = user_pass.split(":")

        rest = parts[1]
        database = rest.split("?")[0].strip("/")
        host_part = rest.split("host=")[1]

        conn = psycopg2.connect(
            host=host_part,
            database=database,
            user=username_db,
            password=password_db
        )
    else:
        # Standard connection
        conn = psycopg2.connect(db_url)

    try:
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            print(f"❌ User with username '{username}' or email '{email}' already exists!")
            return False

        # Hash the password
        hashed_password = get_password_hash(password)

        # Insert the user
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (username, email, hashed_password, full_name or username, True, True, datetime.utcnow(), datetime.utcnow()))

        user_id = cursor.fetchone()[0]
        conn.commit()

        print(f"✅ User created successfully!")
        print(f"   ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name or username}")
        print(f"   Admin: Yes")
        return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_user.py <username> <email> <password> [full_name]")
        print("Example: python create_user.py admin admin@thatglobalview.com MyPassword123 'Admin User'")
        sys.exit(1)

    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    full_name = sys.argv[4] if len(sys.argv) > 4 else None

    create_user(username, email, password, full_name)
