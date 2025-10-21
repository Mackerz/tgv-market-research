"""Tests for CSRF protection"""
import pytest
import time
import os
from unittest.mock import patch

from app.core.csrf import CSRFProtection, generate_csrf_token, verify_csrf_token
from fastapi import HTTPException


class TestCSRFProtection:
    """Tests for CSRFProtection class"""

    def test_generate_token_format(self):
        """Test token generation format"""
        csrf = CSRFProtection()
        token = csrf.generate_token()
        
        # Token should have format: random_token.timestamp
        parts = token.split('.')
        assert len(parts) == 2
        
        # First part should be 43 characters (base64 of 32 bytes)
        assert len(parts[0]) == 43
        
        # Second part should be a valid timestamp
        timestamp = int(parts[1])
        assert timestamp > 0
        current_time = int(time.time())
        assert abs(current_time - timestamp) < 2  # Within 2 seconds

    def test_generate_token_uniqueness(self):
        """Test that generated tokens are unique"""
        csrf = CSRFProtection()
        tokens = set()
        
        for _ in range(100):
            token = csrf.generate_token()
            assert token not in tokens
            tokens.add(token)

    def test_verify_valid_token(self):
        """Test verification of valid token"""
        csrf = CSRFProtection(max_age=3600)
        token = csrf.generate_token()
        
        assert csrf.verify_token(token) is True

    def test_verify_expired_token(self):
        """Test rejection of expired token"""
        csrf = CSRFProtection(max_age=1)  # 1 second expiry
        
        # Create token
        token = csrf.generate_token()
        
        # Wait for expiry
        time.sleep(2)
        
        # Should be expired
        assert csrf.verify_token(token) is False

    def test_verify_invalid_format(self):
        """Test rejection of invalid token formats"""
        csrf = CSRFProtection()
        
        # Missing timestamp
        assert csrf.verify_token("abc123") is False
        
        # Wrong number of parts
        assert csrf.verify_token("abc.123.def") is False
        
        # Invalid timestamp
        assert csrf.verify_token("abc123.notanumber") is False
        
        # Empty token
        assert csrf.verify_token("") is False
        assert csrf.verify_token(None) is False

    def test_verify_wrong_token_length(self):
        """Test rejection of token with wrong length"""
        csrf = CSRFProtection()
        
        # Token too short
        short_token = f"abc.{int(time.time())}"
        assert csrf.verify_token(short_token) is False
        
        # Token too long
        long_token = f"{'a' * 50}.{int(time.time())}"
        assert csrf.verify_token(long_token) is False

    def test_secret_key_from_environment(self):
        """Test loading secret key from environment"""
        with patch.dict(os.environ, {'SECRET_KEY': 'test-secret-key'}):
            csrf = CSRFProtection()
            assert csrf.secret_key == 'test-secret-key'

    def test_default_secret_key(self):
        """Test default secret key when not in environment"""
        with patch.dict(os.environ, {}, clear=True):
            csrf = CSRFProtection()
            assert csrf.secret_key == "change-me-in-production"


class TestVerifyCSRFTokenDependency:
    """Tests for verify_csrf_token FastAPI dependency"""

    @pytest.mark.asyncio
    async def test_csrf_disabled_by_default(self):
        """Test CSRF protection is disabled by default"""
        with patch.dict(os.environ, {'CSRF_PROTECTION_ENABLED': 'false'}):
            result = await verify_csrf_token(None)
            assert result == "csrf-disabled"

    @pytest.mark.asyncio
    async def test_csrf_enabled_requires_token(self):
        """Test CSRF protection requires token when enabled"""
        with patch.dict(os.environ, {'CSRF_PROTECTION_ENABLED': 'true'}):
            with pytest.raises(HTTPException) as exc_info:
                await verify_csrf_token(None)
            
            assert exc_info.value.status_code == 403
            assert "required" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_csrf_enabled_with_valid_token(self):
        """Test CSRF protection accepts valid token"""
        csrf = CSRFProtection()
        valid_token = csrf.generate_token()
        
        with patch.dict(os.environ, {'CSRF_PROTECTION_ENABLED': 'true'}):
            result = await verify_csrf_token(valid_token)
            assert result == valid_token

    @pytest.mark.asyncio
    async def test_csrf_enabled_with_invalid_token(self):
        """Test CSRF protection rejects invalid token"""
        with patch.dict(os.environ, {'CSRF_PROTECTION_ENABLED': 'true'}):
            with pytest.raises(HTTPException) as exc_info:
                await verify_csrf_token("invalid-token")
            
            assert exc_info.value.status_code == 403
            assert "invalid" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_csrf_enabled_with_expired_token(self):
        """Test CSRF protection rejects expired token"""
        # Create token that's already expired
        expired_token = f"{'a' * 43}.{int(time.time()) - 7200}"  # 2 hours ago
        
        with patch.dict(os.environ, {'CSRF_PROTECTION_ENABLED': 'true'}):
            with pytest.raises(HTTPException) as exc_info:
                await verify_csrf_token(expired_token)
            
            assert exc_info.value.status_code == 403


class TestGenerateCSRFTokenHelper:
    """Tests for generate_csrf_token helper function"""

    def test_generate_csrf_token_returns_valid_token(self):
        """Test helper function generates valid token"""
        token = generate_csrf_token()
        
        # Should have correct format
        parts = token.split('.')
        assert len(parts) == 2
        assert len(parts[0]) == 43

    def test_generate_csrf_token_uses_global_instance(self):
        """Test helper uses global CSRFProtection instance"""
        token1 = generate_csrf_token()
        token2 = generate_csrf_token()
        
        # Should be different tokens
        assert token1 != token2
        
        # Both should be valid
        csrf = CSRFProtection()
        assert csrf.verify_token(token1) is True
        assert csrf.verify_token(token2) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
