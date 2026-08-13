"""
Auth service: login and token refresh business logic.
Keeps all auth business rules out of the endpoint layer.
"""
from app.core.exceptions import CredentialsError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.core.config import get_settings
from app.models.domain import USERS_DB, USERNAME_INDEX, UserInDB
from app.schemas.auth import TokenResponse, UserResponse

settings = get_settings()


def authenticate_user(username: str, password: str) -> UserInDB:
    """
    Verify username + password.

    Uses a constant-time comparison to prevent timing attacks —
    always call verify_password even when user doesn't exist (dummy hash).
    """
    user_id = USERNAME_INDEX.get(username.lower())

    # Always run password check to avoid timing-based user enumeration
    _DUMMY_HASH = "$2b$12$invalidhashthatisneverusedXXXXXXXXXXXXXXXXXXXXXX"
    stored_hash = USERS_DB[user_id].hashed_password if user_id else _DUMMY_HASH

    if not verify_password(password, stored_hash) or user_id is None:
        # Identical message whether user exists or password is wrong
        raise CredentialsError("Incorrect username or password")

    user = USERS_DB[user_id]
    if not user.is_active:
        raise CredentialsError("Account is disabled")

    return user


def create_tokens(user: UserInDB) -> TokenResponse:
    """Generate both access and refresh tokens for a user."""
    return TokenResponse(
        access_token=create_access_token(subject=user.id, role=user.role),
        refresh_token=create_refresh_token(subject=user.id),
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


def refresh_access_token(refresh_token: str) -> TokenResponse:
    """
    Validate a refresh token and issue a new access token.

    Only refresh tokens (token_type == 'refresh') are accepted here.
    Access tokens are explicitly rejected.
    """
    payload = decode_token(refresh_token, expected_type="refresh")
    user_id: str = payload["sub"]

    user = USERS_DB.get(user_id)
    if user is None or not user.is_active:
        raise CredentialsError("User not found or account disabled")

    return create_tokens(user)


def get_user_response(user: UserInDB) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )
