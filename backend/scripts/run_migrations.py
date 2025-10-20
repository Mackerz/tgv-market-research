#!/usr/bin/env python3
"""
TMG Market Research - Database Migration Script
Runs Alembic migrations for production deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_migrations():
    """Run Alembic database migrations"""

    # Get database URL using secrets manager
    try:
        from secrets_manager import get_database_url
        database_url = get_database_url()
    except Exception as e:
        print(f"ERROR: Failed to get database URL from secrets manager: {e}")
        # Fallback to environment variable
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("ERROR: DATABASE_URL environment variable is not set")
            sys.exit(1)

    print(f"Running migrations with database URL: {database_url.split('@')[0]}@***")

    try:
        # Change to backend directory
        backend_dir = Path(__file__).parent
        os.chdir(backend_dir)

        # Run migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )

        print("Migrations completed successfully!")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Migration failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()