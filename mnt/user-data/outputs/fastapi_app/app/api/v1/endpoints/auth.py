"""
Auth endpoints: login, token refresh, current user.

All responses use the standard schema — no raw DB models ever returned.
"""
from fastapi import APIRouter, status
from typing import Annotated
from fastapi import Depends

from app.core.dependencies import CurrentUser
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtain JWT tokens",
    description=(
        "Authenticate with username and password. "
        "Returns a short-lived access token (30 min) and a long-lived refresh token (7 days). "
        "Use the access token in the `Authorization: Bearer <token>` header for all protected endpoints."
    ),
    responses={
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
    },
)
def login(body: LoginRequest) -> TokenResponse:
    user = auth_service.authenticate_user(body.username, body.password)
    return auth_service.create_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description=(
        "Exchange a valid refresh token for a new access + refresh token pair. "
        "Refresh tokens are single-use by design — store the new pair after each refresh."
    ),
    responses={
        401: {"description": "Refresh token invalid or expired"},
        422: {"description": "Validation error"},
    },
)
def refresh_token(body: RefreshRequest) -> TokenResponse:
    return auth_service.refresh_access_token(body.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Returns the profile of the currently authenticated user.",
    responses={
        401: {"description": "Not authenticated"},
    },
)
def get_me(current_user: CurrentUser) -> UserResponse:
    return auth_service.get_user_response(current_user)
