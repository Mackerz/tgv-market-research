#!/usr/bin/env python3
"""
Script to create an admin user for the Market Research application.

Usage:
    python create_admin.py --username admin --email admin@example.com --password yourpassword

Or run interactively:
    python create_admin.py
"""

import argparse
import sys
from getpass import getpass

from app.core.database import SessionLocal
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate


def create_admin_user(username: str, email: str, password: str, full_name: str = None):
    """Create an admin user."""
    db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = user_crud.get_by_username(db, username)
        if existing_user:
            print(f"❌ Error: User with username '{username}' already exists")
            return False

        existing_email = user_crud.get_by_email(db, email)
        if existing_email:
            print(f"❌ Error: User with email '{email}' already exists")
            return False

        # Create user
        user_data = UserCreate(
            username=username,
            email=email,
            full_name=full_name or username,
            password=password
        )

        new_user = user_crud.create(db, obj_in=user_data)

        # Set as admin
        new_user.is_admin = True
        db.commit()
        db.refresh(new_user)

        print(f"✅ Successfully created admin user:")
        print(f"   Username: {new_user.username}")
        print(f"   Email: {new_user.email}")
        print(f"   Full Name: {new_user.full_name}")
        print(f"   Admin: {new_user.is_admin}")
        print(f"\n🔑 You can now log in at /login with these credentials")

        return True

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Create an admin user for the Market Research application"
    )
    parser.add_argument("--username", help="Username for the admin user")
    parser.add_argument("--email", help="Email address for the admin user")
    parser.add_argument("--password", help="Password (not recommended for security)")
    parser.add_argument("--full-name", help="Full name of the admin user")

    args = parser.parse_args()

    # Interactive mode if no arguments provided
    if not args.username:
        print("=== Create Admin User ===\n")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        full_name = input("Full Name (optional): ").strip() or None
        password = getpass("Password: ")
        password_confirm = getpass("Confirm Password: ")

        if password != password_confirm:
            print("❌ Error: Passwords do not match")
            sys.exit(1)

        if not username or not email or not password:
            print("❌ Error: Username, email, and password are required")
            sys.exit(1)

    else:
        username = args.username
        email = args.email
        full_name = args.full_name
        password = args.password

        if not password:
            password = getpass(f"Password for {username}: ")
            password_confirm = getpass("Confirm Password: ")

            if password != password_confirm:
                print("❌ Error: Passwords do not match")
                sys.exit(1)

    # Create the user
    success = create_admin_user(username, email, password, full_name)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
