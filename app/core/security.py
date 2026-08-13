"""
Security utilities: JWT tokens and password hashing.

Design decisions:
- Tokens carry sub (user id), role, and token_type (access/refresh).
- Refresh tokens are deliberately scoped — they can ONLY mint new access tokens.
- Passwords are hashed with bcrypt (cost factor 12).
- All errors raise HTTPException so they never expose internals.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import CredentialsError, TokenExpiredError

settings = get_settings()

# bcrypt with cost 12 — good balance of security vs latency on Cloud Run
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


# ── Password ───────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return bcrypt hash of plain-text password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time comparison — safe against timing attacks."""
    return _pwd_context.verify(plain, hashed)


# ── JWT ────────────────────────────────────────────────────────────────────────

def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def create_access_token(subject: str, role: str, extra: dict[str, Any] | None = None) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        subject: User ID (stored in 'sub' claim).
        role: User role string (stored in 'role' claim).
        extra: Any additional claims to embed (optional).

    Returns:
        Signed JWT string.
    """
    expire = _utc_now() + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "token_type": "access",
        "iat": _utc_now(),
        "exp": expire,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived refresh token.
    Refresh tokens carry ONLY sub + token_type — no role, no extra claims.
    """
    expire = _utc_now() + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {
        "sub": subject,
        "token_type": "refresh",
        "iat": _utc_now(),
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: Raw JWT string from Authorization header.
        expected_type: 'access' or 'refresh'. Rejects wrong token types.

    Returns:
        Decoded payload dict.

    Raises:
        TokenExpiredError: Token is past expiry.
        CredentialsError: Token is invalid, malformed, or wrong type.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise CredentialsError("Invalid token")

    token_type = payload.get("token_type")
    if token_type != expected_type:
        raise CredentialsError(
            f"Expected '{expected_type}' token but received '{token_type}' token"
        )

    subject = payload.get("sub")
    if not subject:
        raise CredentialsError("Token missing subject claim")

    return payload
