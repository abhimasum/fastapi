"""
Plant endpoints: full CRUD with role-based access control.

Role requirements:
  GET (list, get)         → viewer, operator, admin
  POST (create)           → operator, admin
  PUT (update)            → operator (own plants only), admin
  DELETE                  → admin only
"""
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated

from app.core.dependencies import (
    CurrentUser,
    require_admin,
    require_operator,
    require_viewer,
)
from app.models.domain import UserInDB
from app.schemas.common import PaginatedResponse
from app.schemas.plant import (
    PlantCreate,
    PlantQueryParams,
    PlantResponse,
    PlantStatus,
    PlantUpdate,
)
from app.services import plant_service

router = APIRouter(prefix="/plants", tags=["Plants"])


@router.get(
    "",
    response_model=PaginatedResponse[PlantResponse],
    status_code=status.HTTP_200_OK,
    summary="List plants",
    description="Returns a paginated list of plant records. Supports filtering by status and minimum uptime.",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient role"},
    },
)
def list_plants(
    current_user: Annotated[UserInDB, Depends(require_viewer)],
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    status: PlantStatus | None = Query(default=None, description="Filter by status"),
    min_uptime: float | None = Query(default=None, ge=0, le=100, description="Minimum uptime %"),
) -> PaginatedResponse[PlantResponse]:
    params = PlantQueryParams(page=page, page_size=page_size, status=status, min_uptime=min_uptime)
    return plant_service.list_plants(params)


@router.post(
    "",
    response_model=PlantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a plant",
    description=(
        "Create a new plant record. "
        "Plant names must be unique (case-insensitive). "
        "Requires `operator` or `admin` role."
    ),
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient role — operator or admin required"},
        409: {"description": "Plant with this name already exists"},
        422: {"description": "Validation error — check field constraints"},
    },
)
def create_plant(
    body: PlantCreate,
    current_user: Annotated[UserInDB, Depends(require_operator)],
) -> PlantResponse:
    return plant_service.create_plant(body, current_user)


@router.get(
    "/{plant_id}",
    response_model=PlantResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a plant by ID",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient role"},
        404: {"description": "Plant not found"},
    },
)
def get_plant(
    plant_id: str,
    current_user: Annotated[UserInDB, Depends(require_viewer)],
) -> PlantResponse:
    return plant_service.get_plant(plant_id)


@router.put(
    "/{plant_id}",
    response_model=PlantResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a plant",
    description=(
        "Partially update a plant (PATCH semantics — only provided fields are updated). "
        "Operators can only update plants they created. Admins can update any plant."
    ),
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient role or ownership"},
        404: {"description": "Plant not found"},
        409: {"description": "Name conflict or business rule violation"},
        422: {"description": "Validation error"},
    },
)
def update_plant(
    plant_id: str,
    body: PlantUpdate,
    current_user: Annotated[UserInDB, Depends(require_operator)],
) -> PlantResponse:
    return plant_service.update_plant(plant_id, body, current_user)


@router.delete(
    "/{plant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a plant",
    description="Permanently delete a plant. **Admin role required.**",
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Admin role required"},
        404: {"description": "Plant not found"},
    },
)
def delete_plant(
    plant_id: str,
    current_user: Annotated[UserInDB, Depends(require_admin)],
) -> None:
    plant_service.delete_plant(plant_id, current_user)
