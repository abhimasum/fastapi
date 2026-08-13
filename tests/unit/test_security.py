"""
Unit tests for app.core.security.

Tests are isolated — no HTTP, no DB, pure function testing.
"""
import time

import pytest
from jose import jwt

from app.core.exceptions import CredentialsError, TokenExpiredError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


# ── Password hashing ───────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_produces_bcrypt_format(self):
        h = hash_password("MySecret123")
        assert h.startswith("$2b$"), "Expected bcrypt hash format"

    def test_verify_correct_password_returns_true(self):
        plain = "SuperSecret@99"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_wrong_password_returns_false(self):
        hashed = hash_password("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False

    def test_same_password_produces_different_hashes(self):
        """bcrypt uses random salt — identical inputs produce different hashes."""
        h1 = hash_password("Same")
        h2 = hash_password("Same")
        assert h1 != h2

    def test_empty_string_hashes_successfully(self):
        """Empty passwords should still hash (API layer rejects them, not this layer)."""
        h = hash_password("")
        assert verify_password("", h) is True

    def test_long_password_hashes_successfully(self):
        long_pw = "A" * 128
        h = hash_password(long_pw)
        assert verify_password(long_pw, h) is True


# ── JWT access tokens ──────────────────────────────────────────────────────────

class TestAccessTokens:
    def test_create_and_decode_access_token(self):
        token = create_access_token(subject="user-123", role="admin")
        payload = decode_token(token, expected_type="access")
        assert payload["sub"] == "user-123"
        assert payload["role"] == "admin"
        assert payload["token_type"] == "access"

    def test_access_token_has_exp_claim(self):
        token = create_access_token(subject="user-1", role="viewer")
        payload = decode_token(token, expected_type="access")
        assert "exp" in payload
        assert "iat" in payload

    def test_extra_claims_are_embedded(self):
        token = create_access_token(subject="u1", role="operator", extra={"plant_ids": ["p1", "p2"]})
        payload = decode_token(token, expected_type="access")
        assert payload["plant_ids"] == ["p1", "p2"]

    def test_tampered_token_raises_credentials_error(self):
        token = create_access_token(subject="user-1", role="admin")
        bad_token = token[:-5] + "XXXXX"
        with pytest.raises(CredentialsError):
            decode_token(bad_token)

    def test_completely_invalid_token_raises_credentials_error(self):
        with pytest.raises(CredentialsError):
            decode_token("not.a.jwt.token")

    def test_empty_token_raises_credentials_error(self):
        with pytest.raises(CredentialsError):
            decode_token("")

    def test_access_token_rejected_as_refresh(self):
        """Access tokens must not be accepted where refresh tokens are expected."""
        token = create_access_token(subject="user-1", role="admin")
        with pytest.raises(CredentialsError, match="Expected 'refresh' token"):
            decode_token(token, expected_type="refresh")


# ── JWT refresh tokens ─────────────────────────────────────────────────────────

class TestRefreshTokens:
    def test_create_and_decode_refresh_token(self):
        token = create_refresh_token(subject="user-abc")
        payload = decode_token(token, expected_type="refresh")
        assert payload["sub"] == "user-abc"
        assert payload["token_type"] == "refresh"

    def test_refresh_token_has_no_role(self):
        """Refresh tokens are intentionally scope-limited — no role claim."""
        token = create_refresh_token(subject="user-abc")
        payload = decode_token(token, expected_type="refresh")
        assert "role" not in payload

    def test_refresh_token_rejected_as_access(self):
        token = create_refresh_token(subject="user-1")
        with pytest.raises(CredentialsError, match="Expected 'access' token"):
            decode_token(token, expected_type="access")

    def test_different_subjects_produce_different_tokens(self):
        t1 = create_refresh_token("user-1")
        t2 = create_refresh_token("user-2")
        assert t1 != t2


# ── Token expiry ───────────────────────────────────────────────────────────────

class TestTokenExpiry:
    def test_expired_token_raises_token_expired_error(self):
        """Create a token with a past expiry using direct jwt.encode."""
        from datetime import datetime, timedelta, timezone
        from app.core.config import get_settings
        settings = get_settings()

        expired_payload = {
            "sub": "user-1",
            "role": "admin",
            "token_type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
            "iat": datetime.now(timezone.utc) - timedelta(minutes=31),
        }
        expired_token = jwt.encode(
            expired_payload, settings.secret_key, algorithm=settings.algorithm
        )
        with pytest.raises(TokenExpiredError):
            decode_token(expired_token, expected_type="access")
