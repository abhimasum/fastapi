from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')


class MessageResponse(BaseModel):
    """Standard success response envelope."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Standard error response envelope."""
    error: str
    detail: Optional[str] = None
    success: bool = False


class PaginatedResponse(BaseModel, Generic[T]):
    """Response envelope for paginated lists."""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    environment: str
