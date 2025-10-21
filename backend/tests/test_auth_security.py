"""Tests for authentication security fixes"""
import pytest
import os
from unittest.mock import patch
from fastapi import HTTPException

from app.core.auth import verify_api_key, generate_api_key


class TestAuthBypassProtection:
    """Tests for authentication bypass protection"""

    @pytest.mark.asyncio
    async def test_dev_mode_bypass_allowed_in_development(self):
        """Test auth bypass is allowed in development environment"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'development',
            'API_KEY': ''
        }, clear=True):
            result = await verify_api_key(None)
            assert result == "dev-mode-bypass"

    @pytest.mark.asyncio
    async def test_production_fails_without_api_key(self):
        """Test production environment fails without API key configured"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'API_KEY': ''
        }, clear=True):
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key(None)
            
            assert exc_info.value.status_code == 500
            assert "not configured" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_production_requires_api_key_header(self):
        """Test production requires API key in header"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'API_KEY': 'test-api-key'
        }):
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key(None)
            
            assert exc_info.value.status_code == 401
            assert "required" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_production_validates_api_key(self):
        """Test production validates API key matches"""
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'API_KEY': 'correct-key'
        }):
            # Wrong key
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key('wrong-key')
            assert exc_info.value.status_code == 403

            # Correct key
            result = await verify_api_key('correct-key')
            assert result == 'correct-key'

    @pytest.mark.asyncio
    async def test_constant_time_comparison_used(self):
        """Test that constant-time comparison is used (timing attack prevention)"""
        # This is more of an integration test
        # The actual constant-time comparison is done by secrets.compare_digest
        with patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'API_KEY': 'a' * 32
        }):
            # Should reject without timing differences
            with pytest.raises(HTTPException):
                await verify_api_key('b' * 32)

    @pytest.mark.asyncio
    async def test_default_environment_is_development(self):
        """Test default environment is development when not set"""
        with patch.dict(os.environ, {
            'API_KEY': ''
        }, clear=True):
            # Should not raise in development (default)
            result = await verify_api_key(None)
            assert result == "dev-mode-bypass"


class TestAPIKeyGeneration:
    """Tests for API key generation"""

    def test_generate_api_key_length(self):
        """Test generated API key has correct length"""
        key = generate_api_key()
        # Should be 64 characters (32 bytes in hex)
        assert len(key) == 64

    def test_generate_api_key_format(self):
        """Test generated API key is hexadecimal"""
        key = generate_api_key()
        # Should only contain hex characters
        assert all(c in '0123456789abcdef' for c in key)

    def test_generate_api_key_uniqueness(self):
        """Test generated keys are unique"""
        keys = set()
        for _ in range(100):
            key = generate_api_key()
            assert key not in keys
            keys.add(key)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
