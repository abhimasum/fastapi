"""
Auth endpoints: login, token refresh, and user profile.

All endpoints except login require a valid JWT access token.
"""
from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser
from app.core.exceptions import CredentialsError
from app.models.domain import UserInDB
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Authenticate with username and password to receive JWT tokens.",
    responses={
        401: {"description": "Invalid credentials"},
    },
)
def login(credentials: LoginRequest) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    user = auth_service.authenticate_user(credentials.username, credentials.password)
    return auth_service.create_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Use a valid refresh token to obtain a new access token.",
    responses={
        401: {"description": "Invalid or expired refresh token"},
    },
)
def refresh_token(request: RefreshRequest) -> TokenResponse:
    """Refresh an expired access token using a valid refresh token."""
    return auth_service.refresh_access_token(request.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current user",
    description="Returns information about the currently authenticated user.",
    responses={
        401: {"description": "Not authenticated"},
    },
)
def get_me(current_user: CurrentUser) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return auth_service.get_user_response(current_user)
