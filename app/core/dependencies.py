"""
FastAPI dependency injection: authentication and role-based access control.

Usage in endpoints:
    @router.get("/plants")
    def list_plants(current_user: CurrentUser = Depends(require_role("viewer"))):
        ...

    @router.delete("/plants/{id}")
    def delete_plant(current_user: CurrentUser = Depends(require_admin)):
        ...
"""
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import CredentialsError, ForbiddenError
from app.core.security import decode_token
from app.models.domain import USERS_DB, UserInDB

# HTTPBearer extracts "Bearer <token>" from the Authorization header.
# auto_error=False lets us return a custom 401 instead of FastAPI's default.
_bearer = HTTPBearer(auto_error=False)


def _get_token(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> str:
    """Extract raw token string from the Authorization header."""
    if credentials is None:
        raise CredentialsError("Authorization header missing")
    return credentials.credentials


def get_current_user(token: str = Depends(_get_token)) -> UserInDB:
    """
    Validate the access JWT and return the authenticated user.

    Raises:
        TokenExpiredError: If token is expired.
        CredentialsError: If token is invalid or user no longer exists.
    """
    payload = decode_token(token, expected_type="access")
    user_id: str = payload["sub"]

    user = USERS_DB.get(user_id)
    if user is None:
        raise CredentialsError("User account not found")
    if not user.is_active:
        raise CredentialsError("User account is disabled")

    return user


# Convenient type alias for endpoint signatures
CurrentUser = Annotated[UserInDB, Depends(get_current_user)]


def require_role(*roles: str):
    """
    Factory that returns a dependency requiring the user to have one of the given roles.

    Usage:
        Depends(require_role("admin", "operator"))
    """
    def _check(current_user: CurrentUser) -> UserInDB:
        if current_user.role not in roles:
            raise ForbiddenError(
                f"This action requires one of these roles: {', '.join(roles)}. "
                f"Your role is: {current_user.role}"
            )
        return current_user
    return _check


# Pre-built role checkers for common patterns
require_viewer   = require_role("viewer", "operator", "admin")
require_operator = require_role("operator", "admin")
require_admin    = require_role("admin")
