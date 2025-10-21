"""Unit tests for CRUD base class"""
import pytest
from app.crud.base import CRUDBase
from pydantic import BaseModel
from typing import Optional
from app.models import user as models


# Test schemas
class UserCreate(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None


class TestCRUDBase:
    """Tests for CRUDBase generic class"""

    @pytest.fixture
    def user_crud(self):
        """Create CRUD instance for User model"""
        return CRUDBase[models.User, UserCreate, UserUpdate](models.User)

    def test_initialization(self, user_crud):
        """Should initialize with model"""
        assert user_crud.model == models.User

    def test_create(self, db_session, user_crud):
        """Should create new record"""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            full_name="Test User"
        )

        user = user_crud.create(db_session, obj_in=user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"

    def test_get(self, db_session, user_crud):
        """Should retrieve record by ID"""
        # Create a user first
        user_data = UserCreate(email="get@example.com", username="getuser")
        created_user = user_crud.create(db_session, obj_in=user_data)

        # Retrieve it
        retrieved_user = user_crud.get(db_session, created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "get@example.com"

    def test_get_not_found(self, db_session, user_crud):
        """Should return None when record not found"""
        user = user_crud.get(db_session, 99999)
        assert user is None

    def test_get_multi(self, db_session, user_crud):
        """Should retrieve multiple records"""
        # Create multiple users
        for i in range(5):
            user_data = UserCreate(
                email=f"user{i}@example.com",
                username=f"user{i}"
            )
            user_crud.create(db_session, obj_in=user_data)

        # Retrieve all
        users = user_crud.get_multi(db_session, skip=0, limit=100)

        assert len(users) == 5

    def test_get_multi_with_pagination(self, db_session, user_crud):
        """Should support pagination"""
        # Create 10 users
        for i in range(10):
            user_data = UserCreate(
                email=f"user{i}@example.com",
                username=f"user{i}"
            )
            user_crud.create(db_session, obj_in=user_data)

        # Get first page
        page1 = user_crud.get_multi(db_session, skip=0, limit=5)
        assert len(page1) == 5

        # Get second page
        page2 = user_crud.get_multi(db_session, skip=5, limit=5)
        assert len(page2) == 5

        # Verify they're different
        page1_ids = {u.id for u in page1}
        page2_ids = {u.id for u in page2}
        assert page1_ids.isdisjoint(page2_ids)

    def test_update_with_pydantic_model(self, db_session, user_crud):
        """Should update record using Pydantic model"""
        # Create user
        user_data = UserCreate(email="old@example.com", username="olduser")
        user = user_crud.create(db_session, obj_in=user_data)

        # Update
        update_data = UserUpdate(email="new@example.com", full_name="Updated Name")
        updated_user = user_crud.update(db_session, db_obj=user, obj_in=update_data)

        assert updated_user.email == "new@example.com"
        assert updated_user.full_name == "Updated Name"
        assert updated_user.username == "olduser"  # Unchanged

    def test_update_with_dict(self, db_session, user_crud):
        """Should update record using dictionary"""
        # Create user
        user_data = UserCreate(email="dict@example.com", username="dictuser")
        user = user_crud.create(db_session, obj_in=user_data)

        # Update with dict
        update_dict = {"full_name": "Dict Update"}
        updated_user = user_crud.update(db_session, db_obj=user, obj_in=update_dict)

        assert updated_user.full_name == "Dict Update"

    def test_update_partial(self, db_session, user_crud):
        """Should support partial updates"""
        # Create user
        user_data = UserCreate(
            email="partial@example.com",
            username="partialuser",
            full_name="Original Name"
        )
        user = user_crud.create(db_session, obj_in=user_data)

        # Update only username
        update_data = UserUpdate(username="newusername")
        updated_user = user_crud.update(db_session, db_obj=user, obj_in=update_data)

        assert updated_user.username == "newusername"
        assert updated_user.email == "partial@example.com"  # Unchanged
        assert updated_user.full_name == "Original Name"  # Unchanged

    def test_update_by_id_success(self, db_session, user_crud):
        """Should update record by ID"""
        # Create user
        user_data = UserCreate(email="byid@example.com", username="byiduser")
        user = user_crud.create(db_session, obj_in=user_data)

        # Update by ID
        update_data = UserUpdate(full_name="Updated By ID")
        updated_user = user_crud.update_by_id(
            db_session, id=user.id, obj_in=update_data
        )

        assert updated_user is not None
        assert updated_user.full_name == "Updated By ID"

    def test_update_by_id_not_found(self, db_session, user_crud):
        """Should return None when updating non-existent record"""
        update_data = UserUpdate(full_name="No Such User")
        result = user_crud.update_by_id(db_session, id=99999, obj_in=update_data)

        assert result is None

    def test_delete_success(self, db_session, user_crud):
        """Should delete record"""
        # Create user
        user_data = UserCreate(email="delete@example.com", username="deleteuser")
        user = user_crud.create(db_session, obj_in=user_data)

        # Delete
        success = user_crud.delete(db_session, id=user.id)
        assert success is True

        # Verify deleted
        deleted_user = user_crud.get(db_session, user.id)
        assert deleted_user is None

    def test_delete_not_found(self, db_session, user_crud):
        """Should return False when deleting non-existent record"""
        success = user_crud.delete(db_session, id=99999)
        assert success is False

    def test_exists_true(self, db_session, user_crud):
        """Should return True when record exists"""
        # Create user
        user_data = UserCreate(email="exists@example.com", username="existsuser")
        user = user_crud.create(db_session, obj_in=user_data)

        # Check existence
        exists = user_crud.exists(db_session, id=user.id)
        assert exists is True

    def test_exists_false(self, db_session, user_crud):
        """Should return False when record doesn't exist"""
        exists = user_crud.exists(db_session, id=99999)
        assert exists is False


class TestCRUDBaseExtension:
    """Tests for extending CRUDBase"""

    class ExtendedUserCRUD(CRUDBase[models.User, UserCreate, UserUpdate]):
        """Extended CRUD with custom method"""

        def get_by_email(self, db, email: str):
            """Custom method to get user by email"""
            return db.query(self.model).filter(
                self.model.email == email
            ).first()

    @pytest.fixture
    def extended_crud(self):
        """Create extended CRUD instance"""
        return self.ExtendedUserCRUD(models.User)

    def test_inherits_base_methods(self, db_session, extended_crud):
        """Should inherit all base CRUD methods"""
        user_data = UserCreate(email="inherit@example.com", username="inherituser")
        user = extended_crud.create(db_session, obj_in=user_data)

        assert user.id is not None
        assert extended_crud.get(db_session, user.id) is not None

    def test_custom_method_works(self, db_session, extended_crud):
        """Custom methods should work alongside inherited ones"""
        user_data = UserCreate(email="custom@example.com", username="customuser")
        extended_crud.create(db_session, obj_in=user_data)

        # Use custom method
        user = extended_crud.get_by_email(db_session, "custom@example.com")

        assert user is not None
        assert user.email == "custom@example.com"


class TestCRUDBaseIntegration:
    """Integration tests for CRUDBase"""

    def test_complete_crud_workflow(self, db_session):
        """Should handle complete CRUD workflow"""
        user_crud = CRUDBase[models.User, UserCreate, UserUpdate](models.User)

        # Create
        user_data = UserCreate(
            email="workflow@example.com",
            username="workflowuser",
            full_name="Workflow Test"
        )
        user = user_crud.create(db_session, obj_in=user_data)
        assert user.id is not None

        # Read
        retrieved = user_crud.get(db_session, user.id)
        assert retrieved.email == "workflow@example.com"

        # Update
        update_data = UserUpdate(full_name="Updated Workflow")
        updated = user_crud.update(db_session, db_obj=retrieved, obj_in=update_data)
        assert updated.full_name == "Updated Workflow"

        # Delete
        success = user_crud.delete(db_session, id=user.id)
        assert success is True

        # Verify deletion
        assert user_crud.get(db_session, user.id) is None

    def test_multiple_models_with_same_pattern(self, db_session):
        """Should work with different models using same pattern"""
        user_crud = CRUDBase[models.User, UserCreate, UserUpdate](models.User)
        post_crud = CRUDBase[models.Post, dict, dict](models.Post)

        # Create user
        user_data = UserCreate(email="multi@example.com", username="multiuser")
        user = user_crud.create(db_session, obj_in=user_data)

        # Create post
        post_data = {
            "title": "Test Post",
            "content": "Test content",
            "author_id": user.id
        }
        post = post_crud.create(db_session, obj_in=post_data)

        assert user.id is not None
        assert post.id is not None
        assert post.author_id == user.id
