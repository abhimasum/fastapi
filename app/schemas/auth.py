"""
Auth-related request and response schemas.
All validation errors become 422 responses automatically via Pydantic v2.
"""
import re

from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Credentials submitted for authentication."""
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        examples=["admin"],
        description="Username (alphanumeric + underscore, 3-50 chars)",
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        examples=["Admin@123"],
        description="Password (min 8 chars)",
    )

    @field_validator("username")
    @classmethod
    def username_no_whitespace(cls, v: str) -> str:
        if v != v.strip():
            raise ValueError("Username must not have leading or trailing spaces")
        return v.lower()


class RefreshRequest(BaseModel):
    """Token submitted to get a new access token."""
    refresh_token: str = Field(description="Valid refresh JWT token")


class TokenResponse(BaseModel):
    """Returned after successful login or token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token lifetime in seconds")


class UserResponse(BaseModel):
    """Public user representation — no password hash, no internal IDs."""
    id: str
    username: str
    email: str
    role: str
    is_active: bool
