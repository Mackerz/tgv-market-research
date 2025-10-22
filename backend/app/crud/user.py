"""User and Post CRUD operations using CRUDBase"""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models.user import User, Post
from app.schemas.user import UserCreate, UserUpdate, PostCreate, PostUpdate
from app.core.auth import get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model"""

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(self.model).filter(self.model.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(self.model).filter(self.model.username == username).first()

    def get_by_google_id(self, db: Session, google_id: str) -> Optional[User]:
        """Get user by Google ID"""
        return db.query(self.model).filter(self.model.google_id == google_id).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create user with hashed password"""
        obj_in_data = obj_in.model_dump()
        password = obj_in_data.pop("password", None)
        db_obj = User(**obj_in_data)
        if password:
            db_obj.hashed_password = get_password_hash(password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_google_user(
        self, db: Session, *, email: str, username: str, full_name: str, google_id: str
    ) -> User:
        """Create user from Google SSO"""
        db_obj = User(
            email=email,
            username=username,
            full_name=full_name,
            google_id=google_id,
            is_active=True,
            is_admin=False,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
    """CRUD operations for Post model"""

    def get_multi_by_author(
        self, db: Session, *, author_id: int, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """Get posts by author"""
        return (
            db.query(self.model)
            .filter(self.model.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_published(
        self, db: Session, *, skip: int = 0, limit: int = 100, published_only: bool = False
    ) -> List[Post]:
        """Get posts with optional published filter"""
        query = db.query(self.model)
        if published_only:
            query = query.filter(self.model.published == True)
        return query.offset(skip).limit(limit).all()

    def create_with_author(
        self, db: Session, *, obj_in: PostCreate, author_id: int
    ) -> Post:
        """Create post with author ID"""
        obj_in_data = obj_in.dict()
        obj_in_data['author_id'] = author_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create singleton instances
user = CRUDUser(User)
post = CRUDPost(Post)


# Backward compatibility - maintain old function signatures
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return user.get(db, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return user.get_by_email(db, email)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return user.get_by_username(db, username)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get multiple users"""
    return user.get_multi(db, skip=skip, limit=limit)


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create user"""
    return user.create(db, obj_in=user_data)


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Update user"""
    return user.update_by_id(db, id=user_id, obj_in=user_data)


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    return user.delete(db, id=user_id)


# Post functions
def get_post(db: Session, post_id: int) -> Optional[Post]:
    """Get post by ID"""
    return post.get(db, post_id)


def get_posts(db: Session, skip: int = 0, limit: int = 100, published_only: bool = False) -> List[Post]:
    """Get multiple posts"""
    return post.get_multi_published(db, skip=skip, limit=limit, published_only=published_only)


def get_posts_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
    """Get posts by author"""
    return post.get_multi_by_author(db, author_id=author_id, skip=skip, limit=limit)


def create_post(db: Session, post_data: PostCreate, author_id: int) -> Post:
    """Create post"""
    return post.create_with_author(db, obj_in=post_data, author_id=author_id)


def update_post(db: Session, post_id: int, post_data: PostUpdate) -> Optional[Post]:
    """Update post"""
    return post.update_by_id(db, id=post_id, obj_in=post_data)


def delete_post(db: Session, post_id: int) -> bool:
    """Delete post"""
    return post.delete(db, id=post_id)
