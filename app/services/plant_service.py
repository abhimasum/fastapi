"""
Plant service: all CRUD operations and business rules for Plant resources.
"""
import uuid
from datetime import datetime, timezone

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.domain import PLANTS_DB, PlantInDB, UserInDB
from app.schemas.common import PaginatedResponse
from app.schemas.plant import PlantCreate, PlantQueryParams, PlantResponse, PlantUpdate


def _to_response(plant: PlantInDB) -> PlantResponse:
    return PlantResponse(**plant.model_dump())


def list_plants(params: PlantQueryParams) -> PaginatedResponse[PlantResponse]:
    """Return a filtered, paginated list of plants."""
    all_plants = list(PLANTS_DB.values())

    # Apply filters
    if params.status:
        all_plants = [p for p in all_plants if p.status == params.status]
    if params.min_uptime is not None:
        all_plants = [p for p in all_plants if p.uptime_percent >= params.min_uptime]

    # Sort deterministically
    all_plants.sort(key=lambda p: p.created_at)

    total = len(all_plants)
    start = (params.page - 1) * params.page_size
    end = start + params.page_size
    page_items = all_plants[start:end]
    
    # Calculate total pages
    pages = (total + params.page_size - 1) // params.page_size  # Ceiling division

    return PaginatedResponse(
        items=[_to_response(p) for p in page_items],
        total=total,
        page=params.page,
        size=params.page_size,
        pages=pages,
    )


def get_plant(plant_id: str) -> PlantResponse:
    """Fetch a single plant by ID."""
    plant = PLANTS_DB.get(plant_id)
    if plant is None:
        raise NotFoundError(f"Plant '{plant_id}' not found")
    return _to_response(plant)


def create_plant(data: PlantCreate, current_user: UserInDB) -> PlantResponse:
    """
    Create a new plant record.
    Rejects duplicate names (case-insensitive) to prevent accidental duplicates.
    """
    # Business rule: names must be unique (case-insensitive)
    existing_names = {p.name.lower() for p in PLANTS_DB.values()}
    if data.name.lower() in existing_names:
        raise ConflictError(f"A plant named '{data.name}' already exists")

    plant_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    plant = PlantInDB(
        id=plant_id,
        name=data.name,
        location=data.location,
        status=data.status,
        capacity_kw=data.capacity_kw,
        uptime_percent=data.uptime_percent,
        owner_id=current_user.id,
        created_at=now,
        updated_at=now,
    )
    PLANTS_DB[plant_id] = plant
    return _to_response(plant)


def update_plant(plant_id: str, data: PlantUpdate, current_user: UserInDB) -> PlantResponse:
    """
    Partially update a plant.
    Only admins can update plants owned by others.
    """
    plant = PLANTS_DB.get(plant_id)
    if plant is None:
        raise NotFoundError(f"Plant '{plant_id}' not found")

    # Ownership check: operators can only update their own plants
    if current_user.role == "operator" and plant.owner_id != current_user.id:
        raise ForbiddenError("Operators can only update their own plants")

    # Check name uniqueness if name is being changed
    if data.name is not None and data.name.lower() != plant.name.lower():
        existing_names = {
            p.name.lower() for pid, p in PLANTS_DB.items() if pid != plant_id
        }
        if data.name.lower() in existing_names:
            raise ConflictError(f"A plant named '{data.name}' already exists")

    # Apply partial updates — only override non-None fields
    update_dict = data.model_dump(exclude_none=True)
    updated_plant = plant.model_copy(
        update={**update_dict, "updated_at": datetime.now(timezone.utc)}
    )

    # Validate offline/uptime invariant after applying updates
    if updated_plant.status == "offline" and updated_plant.uptime_percent > 0:
        raise ConflictError(
            "Cannot set status to 'offline' while uptime_percent is > 0. "
            "Set uptime_percent to 0 first."
        )

    PLANTS_DB[plant_id] = updated_plant
    return _to_response(updated_plant)


def delete_plant(plant_id: str, current_user: UserInDB) -> None:
    """
    Delete a plant. Only admins can delete any plant.
    """
    plant = PLANTS_DB.get(plant_id)
    if plant is None:
        raise NotFoundError(f"Plant '{plant_id}' not found")

    del PLANTS_DB[plant_id]
