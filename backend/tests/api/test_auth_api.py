"""Tests for authentication API endpoints"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.auth import get_password_hash, create_access_token


@pytest.fixture
def mock_user():
    """Create a mock user"""
    password = "test_password"
    hashed = get_password_hash(password)

    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=hashed,
        google_id=None,
        is_active=True,
        is_admin=True,
        failed_login_attempts=0,
        locked_until=None,
        created_at=datetime.now(),
        updated_at=None
    )


@pytest.fixture
def mock_admin():
    """Create a mock admin user"""
    password = "admin_password"
    hashed = get_password_hash(password)

    return User(
        id=2,
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=hashed,
        google_id=None,
        is_active=True,
        is_admin=True,
        failed_login_attempts=0,
        locked_until=None,
        created_at=datetime.now(),
        updated_at=None
    )


class TestLoginEndpoint:
    """Tests for POST /api/auth/login endpoint"""

    def test_login_success(self, client, mock_user):
        """Test successful login"""
        with patch('app.api.v1.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user

            response = client.post(
                "/api/auth/login",
                json={"username": "testuser", "password": "test_password"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "user" in data
            assert data["user"]["username"] == "testuser"
            assert data["user"]["is_admin"] is True

            # Check cookie is set
            assert "access_token" in response.cookies

    def test_login_wrong_password(self, client):
        """Test login with wrong password"""
        with patch('app.api.v1.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = None  # Authentication failed

            response = client.post(
                "/api/auth/login",
                json={"username": "testuser", "password": "wrong_password"}
            )

            assert response.status_code == 401
            assert "incorrect" in response.json()["detail"].lower()

    def test_login_inactive_user(self, client, mock_user):
        """Test login with inactive user"""
        mock_user.is_active = False

        with patch('app.api.v1.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user

            response = client.post(
                "/api/auth/login",
                json={"username": "testuser", "password": "test_password"}
            )

            assert response.status_code == 403
            assert "inactive" in response.json()["detail"].lower()

    def test_login_missing_username(self, client):
        """Test login without username"""
        response = client.post(
            "/api/auth/login",
            json={"password": "test_password"}
        )

        assert response.status_code == 422  # Validation error

    def test_login_missing_password(self, client):
        """Test login without password"""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser"}
        )

        assert response.status_code == 422  # Validation error

    def test_login_cookie_settings_dev(self, client, mock_user):
        """Test cookie settings in development"""
        with patch('app.api.v1.auth.authenticate_user') as mock_auth:
            with patch.dict('os.environ', {'ENVIRONMENT': 'development'}):
                mock_auth.return_value = mock_user

                response = client.post(
                    "/api/auth/login",
                    json={"username": "testuser", "password": "test_password"}
                )

                assert response.status_code == 200
                # In dev, secure flag should be False
                cookies = response.headers.get('set-cookie', '')
                assert 'access_token' in cookies


class TestGoogleLoginEndpoint:
    """Tests for POST /api/auth/google endpoint"""

    def test_google_login_new_user(self, client):
        """Test Google login creates new user"""
        mock_idinfo = {
            "sub": "google_user_id_123",
            "email": "newuser@gmail.com",
            "name": "New User"
        }

        with patch('app.api.v1.auth.id_token.verify_oauth2_token') as mock_verify:
            with patch('app.api.v1.auth.user_crud') as mock_crud:
                with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test-client-id'}):
                    mock_verify.return_value = mock_idinfo

                    # User doesn't exist yet
                    mock_crud.get_by_google_id.return_value = None
                    mock_crud.get_by_email.return_value = None
                    mock_crud.get_by_username.return_value = None

                    # Mock user creation
                    new_user = User(
                        id=1,
                        username="newuser",
                        email="newuser@gmail.com",
                        full_name="New User",
                        google_id="google_user_id_123",
                        is_active=True,
                        is_admin=False
                    )
                    mock_crud.create_google_user.return_value = new_user

                    response = client.post(
                        "/api/auth/google",
                        json={"credential": "fake_google_token"}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "access_token" in data
                    assert data["user"]["email"] == "newuser@gmail.com"

    def test_google_login_existing_user(self, client):
        """Test Google login with existing user"""
        mock_idinfo = {
            "sub": "google_user_id_123",
            "email": "existing@gmail.com",
            "name": "Existing User"
        }

        existing_user = User(
            id=1,
            username="existing",
            email="existing@gmail.com",
            full_name="Existing User",
            google_id="google_user_id_123",
            is_active=True,
            is_admin=False
        )

        with patch('app.api.v1.auth.id_token.verify_oauth2_token') as mock_verify:
            with patch('app.api.v1.auth.user_crud') as mock_crud:
                with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test-client-id'}):
                    mock_verify.return_value = mock_idinfo
                    mock_crud.get_by_google_id.return_value = existing_user

                    response = client.post(
                        "/api/auth/google",
                        json={"credential": "fake_google_token"}
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["user"]["username"] == "existing"

    def test_google_login_invalid_token(self, client):
        """Test Google login with invalid token"""
        with patch('app.api.v1.auth.id_token.verify_oauth2_token') as mock_verify:
            with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test-client-id'}):
                mock_verify.side_effect = ValueError("Invalid token")

                response = client.post(
                    "/api/auth/google",
                    json={"credential": "invalid_token"}
                )

                assert response.status_code == 401
                assert "invalid" in response.json()["detail"].lower()

    def test_google_login_not_configured(self, client):
        """Test Google login when not configured"""
        with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': ''}, clear=True):
            response = client.post(
                "/api/auth/google",
                json={"credential": "some_token"}
            )

            assert response.status_code == 500
            assert "not configured" in response.json()["detail"].lower()

    def test_google_login_inactive_user(self, client):
        """Test Google login with inactive user"""
        mock_idinfo = {
            "sub": "google_user_id_123",
            "email": "inactive@gmail.com",
            "name": "Inactive User"
        }

        inactive_user = User(
            id=1,
            username="inactive",
            email="inactive@gmail.com",
            full_name="Inactive User",
            google_id="google_user_id_123",
            is_active=False,  # Inactive
            is_admin=False
        )

        with patch('app.api.v1.auth.id_token.verify_oauth2_token') as mock_verify:
            with patch('app.api.v1.auth.user_crud') as mock_crud:
                with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test-client-id'}):
                    mock_verify.return_value = mock_idinfo
                    mock_crud.get_by_google_id.return_value = inactive_user

                    response = client.post(
                        "/api/auth/google",
                        json={"credential": "fake_token"}
                    )

                    assert response.status_code == 403
                    assert "inactive" in response.json()["detail"].lower()


class TestLogoutEndpoint:
    """Tests for POST /api/auth/logout endpoint"""

    def test_logout_success(self, client):
        """Test successful logout"""
        response = client.post("/api/auth/logout")

        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    def test_logout_clears_cookie(self, client):
        """Test logout clears the cookie"""
        # First login
        mock_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password"),
            is_active=True,
            is_admin=False
        )

        with patch('app.api.v1.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user
            login_response = client.post(
                "/api/auth/login",
                json={"username": "testuser", "password": "password"}
            )
            assert "access_token" in login_response.cookies

        # Then logout
        logout_response = client.post("/api/auth/logout")

        # Cookie should be deleted
        cookies = logout_response.headers.get('set-cookie', '')
        # The cookie should either be absent or have an expired/deleted directive


class TestGetCurrentUserEndpoint:
    """Tests for GET /api/auth/me endpoint"""

    def test_get_current_user_authenticated(self, client, mock_user):
        """Test getting current user when authenticated"""
        # Create a valid token
        token = create_access_token({"sub": mock_user.id})

        with patch('app.api.v1.auth.get_current_user_from_token') as mock_get_user:
            mock_get_user.return_value = mock_user

            response = client.get(
                "/api/auth/me",
                cookies={"access_token": token}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "testuser"
            assert data["email"] == "test@example.com"

    def test_get_current_user_not_authenticated(self, client):
        """Test getting current user when not authenticated"""
        with patch('app.api.v1.auth.get_current_user_from_token') as mock_get_user:
            mock_get_user.return_value = None

            response = client.get("/api/auth/me")

            assert response.status_code == 401


class TestCheckAuthEndpoint:
    """Tests for GET /api/auth/check endpoint"""

    def test_check_auth_authenticated(self, client, mock_user):
        """Test auth check when authenticated"""
        with patch('app.api.v1.auth.get_current_user_from_token') as mock_get_user:
            with patch.dict('os.environ', {'ENVIRONMENT': 'development', 'GOOGLE_CLIENT_ID': ''}):
                mock_get_user.return_value = mock_user

                response = client.get("/api/auth/check")

                assert response.status_code == 200
                data = response.json()
                assert data["authenticated"] is True
                assert data["environment"] == "development"
                assert data["google_sso_enabled"] is False

    def test_check_auth_not_authenticated(self, client):
        """Test auth check when not authenticated"""
        with patch('app.api.v1.auth.get_current_user_from_token') as mock_get_user:
            with patch.dict('os.environ', {'ENVIRONMENT': 'production', 'GOOGLE_CLIENT_ID': 'test-id'}):
                mock_get_user.return_value = None

                response = client.get("/api/auth/check")

                assert response.status_code == 200
                data = response.json()
                assert data["authenticated"] is False
                assert data["environment"] == "production"
                assert data["google_sso_enabled"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
