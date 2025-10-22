"""Tests for session-based authentication (JWT)"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi import HTTPException
from jose import jwt

from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user_from_token,
    require_auth,
    require_admin,
    SECRET_KEY,
    ALGORITHM,
)
from app.models.user import User


class TestPasswordHashing:
    """Tests for password hashing and verification"""

    def test_password_hash_is_different_from_plain(self):
        """Test that hashed password is different from plain text"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_password_hash_is_consistent(self):
        """Test that same password can be verified"""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed)

    def test_wrong_password_fails_verification(self):
        """Test that wrong password fails verification"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        assert not verify_password(wrong_password, hashed)

    def test_empty_password_handling(self):
        """Test handling of empty passwords"""
        password = ""
        hashed = get_password_hash(password)

        assert verify_password(password, hashed)
        assert not verify_password("not_empty", hashed)

    def test_unicode_password_support(self):
        """Test that unicode passwords are supported"""
        password = "пароль123🔒"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed)

    def test_password_hashes_are_unique(self):
        """Test that same password generates different hashes (salted)"""
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_invalid_hash_format_returns_false(self):
        """Test that invalid hash format returns False instead of crashing"""
        password = "test_password"
        invalid_hash = "not_a_valid_hash"

        assert not verify_password(password, invalid_hash)


class TestJWTTokens:
    """Tests for JWT token creation and validation"""

    def test_create_access_token_basic(self):
        """Test basic token creation"""
        data = {"sub": 1}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_user_id(self):
        """Test that token contains the user ID"""
        user_id = 42
        data = {"sub": user_id}
        token = create_access_token(data)

        # Decode token (without validation to check raw payload)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False})
        # JWT spec requires sub to be a string
        assert payload["sub"] == str(user_id)

    def test_token_has_expiration(self):
        """Test that token has expiration time"""
        data = {"sub": 1}
        token = create_access_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False})
        assert "exp" in payload
        assert isinstance(payload["exp"], int)

    def test_custom_expiration_time(self):
        """Test custom expiration time works differently than default"""
        # Create token with custom expiration
        data = {"sub": 1}
        custom_delta = timedelta(hours=1)
        token_custom = create_access_token(data, custom_delta)

        # Create token with default expiration
        token_default = create_access_token(data)

        # Decode both tokens
        payload_custom = jwt.decode(token_custom, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False})
        payload_default = jwt.decode(token_default, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False})

        # Custom expiration should be different from default
        # and should be earlier (shorter duration)
        assert payload_custom["exp"] < payload_default["exp"]

        # Verify custom expiration is reasonable (within 2 hours)
        now_timestamp = datetime.utcnow().timestamp()
        time_until_exp = payload_custom["exp"] - now_timestamp
        # Less than 2 hours
        assert 0 < time_until_exp < 2 * 3600, \
            f"Expected expiration within 2 hours, got {time_until_exp / 3600} hours"

    def test_expired_token_raises_error(self):
        """Test that expired token raises error"""
        data = {"sub": 1}
        # Create token that expired 1 hour ago
        expires_delta = timedelta(hours=-1)
        token = create_access_token(data, expires_delta)

        # Should raise error when decoding
        with pytest.raises(Exception):  # jose.JWTError or similar
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    def test_tampered_token_fails_validation(self):
        """Test that tampered token fails validation"""
        data = {"sub": 1}
        token = create_access_token(data)

        # Tamper with the token
        tampered_token = token[:-10] + "tampered12"

        with pytest.raises(Exception):
            jwt.decode(tampered_token, SECRET_KEY, algorithms=[ALGORITHM])


class TestUserAuthentication:
    """Tests for user authentication"""

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        # Mock database and user
        mock_db = Mock()
        password = "test_password"
        hashed = get_password_hash(password)

        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=hashed,
            is_active=True,
            is_admin=False
        )

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Authenticate
        result = authenticate_user(mock_db, "testuser", password)

        assert result is not None
        assert result.username == "testuser"

    def test_authenticate_user_wrong_password(self):
        """Test authentication fails with wrong password"""
        mock_db = Mock()
        password = "correct_password"
        hashed = get_password_hash(password)

        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=hashed,
            is_active=True,
            is_admin=False
        )

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Try wrong password
        result = authenticate_user(mock_db, "testuser", "wrong_password")

        assert result is None

    def test_authenticate_user_not_found(self):
        """Test authentication fails when user not found"""
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = authenticate_user(mock_db, "nonexistent", "password")

        assert result is None

    def test_authenticate_google_user_without_password(self):
        """Test that Google SSO users without password cannot use password auth"""
        mock_db = Mock()

        # User created via Google SSO (no password)
        mock_user = User(
            id=1,
            username="googleuser",
            email="google@example.com",
            hashed_password=None,  # No password set
            google_id="google123",
            is_active=True,
            is_admin=False
        )

        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = authenticate_user(mock_db, "googleuser", "any_password")

        assert result is None


class TestGetCurrentUser:
    """Tests for getting current user from token"""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test getting current user with valid token"""
        # Create a valid token
        user_id = 1
        token = create_access_token({"sub": user_id})

        # Mock database
        mock_db = Mock()
        mock_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            is_active=True,
            is_admin=False
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Get user from token
        result = await get_current_user_from_token(token=token, db=mock_db)

        assert result is not None
        assert result.id == user_id

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self):
        """Test getting current user without token"""
        mock_db = Mock()

        result = await get_current_user_from_token(token=None, db=mock_db)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        mock_db = Mock()

        result = await get_current_user_from_token(token="invalid_token", db=mock_db)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        """Test getting current user when user deleted from database"""
        user_id = 999
        token = create_access_token({"sub": user_id})

        # Mock database - user not found
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = await get_current_user_from_token(token=token, db=mock_db)

        assert result is None


class TestRequireAuth:
    """Tests for require_auth dependency"""

    @pytest.mark.asyncio
    async def test_require_auth_with_valid_user(self):
        """Test require_auth with authenticated user"""
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            is_active=True,
            is_admin=False
        )

        result = await require_auth(current_user=mock_user, api_key=None)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_require_auth_without_user_raises_401(self):
        """Test require_auth without user raises 401"""
        with pytest.raises(HTTPException) as exc_info:
            await require_auth(current_user=None, api_key=None)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_auth_inactive_user_raises_403(self):
        """Test require_auth with inactive user raises 403"""
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            is_active=False,  # Inactive
            is_admin=False
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_auth(current_user=mock_user, api_key=None)

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_auth_with_valid_api_key(self):
        """Test require_auth accepts valid API key"""
        with patch.dict('os.environ', {'API_KEY': 'test-key', 'ENVIRONMENT': 'production'}):
            result = await require_auth(current_user=None, api_key='test-key')

            # Should return a fake admin user
            assert result is not None
            assert result.is_admin is True

    @pytest.mark.asyncio
    async def test_require_auth_dev_mode_api_key(self):
        """Test require_auth in dev mode without API key"""
        with patch.dict('os.environ', {'ENVIRONMENT': 'development', 'API_KEY': ''}):
            result = await require_auth(current_user=None, api_key='any-key')

            # Should return fake dev admin user
            assert result is not None
            assert result.is_admin is True


class TestRequireAdmin:
    """Tests for require_admin dependency"""

    @pytest.mark.asyncio
    async def test_require_admin_with_admin_user(self):
        """Test require_admin with admin user"""
        mock_user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            is_active=True,
            is_admin=True  # Is admin
        )

        result = await require_admin(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_require_admin_with_non_admin_raises_403(self):
        """Test require_admin with non-admin user raises 403"""
        mock_user = User(
            id=1,
            username="user",
            email="user@example.com",
            is_active=True,
            is_admin=False  # Not admin
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "admin" in exc_info.value.detail.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
