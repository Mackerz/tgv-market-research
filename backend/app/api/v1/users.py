"""User and Post API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas import user as schemas
from app.crud import user as crud
from app.dependencies import get_user_or_404, get_post_or_404

router = APIRouter(prefix="/api", tags=["users", "posts"])


# =============================================================================
# USER ENDPOINTS
# =============================================================================

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    return crud.create_user(db=db, user=user)


@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schemas.UserWithPosts)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    # Get user using dependency helper
    return get_user_or_404(user_id, db)


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update a user"""
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    success = crud.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


# =============================================================================
# POST ENDPOINTS
# =============================================================================

@router.post("/users/{user_id}/posts/", response_model=schemas.Post)
def create_post_for_user(user_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Create a post for a specific user"""
    # Check if user exists using dependency helper
    get_user_or_404(user_id, db)

    return crud.create_post(db=db, post=post, author_id=user_id)


@router.get("/posts/", response_model=List[schemas.PostWithAuthor])
def read_posts(skip: int = 0, limit: int = 100, published_only: bool = False, db: Session = Depends(get_db)):
    """Get all posts"""
    posts = crud.get_posts(db, skip=skip, limit=limit, published_only=published_only)
    return posts


@router.get("/posts/{post_id}", response_model=schemas.PostWithAuthor)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID"""
    # Get post using dependency helper
    return get_post_or_404(post_id, db)


@router.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostUpdate, db: Session = Depends(get_db)):
    """Update a post"""
    db_post = crud.update_post(db=db, post_id=post_id, post=post)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post"""
    success = crud.delete_post(db=db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}
