"""
Plant resource schemas with strict Pydantic v2 validation.

Design:
- PlantCreate: fields required for creation.
- PlantUpdate: all optional — PATCH semantics (only update what's provided).
- PlantResponse: what gets returned to clients.
"""
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

PlantStatus = Literal["operational", "maintenance", "offline", "error"]

# Reusable constrained types
PlantName = Annotated[str, Field(min_length=2, max_length=100)]
Location  = Annotated[str, Field(min_length=2, max_length=200)]
CapacityKW = Annotated[float, Field(gt=0, le=1_000_000, description="Capacity in kilowatts (0–1,000,000)")]
UptimePct  = Annotated[float, Field(ge=0.0, le=100.0, description="Uptime percentage (0–100)")]


class PlantCreate(BaseModel):
    """Request body for creating a new plant record."""
    name: PlantName = Field(
        examples=["Bosch Plant Stuttgart-A"],
        description="Plant display name (2–100 chars)",
    )
    location: Location = Field(
        examples=["Stuttgart, Germany"],
        description="Physical location of the plant",
    )
    status: PlantStatus = Field(
        default="operational",
        description="Current operational status",
    )
    capacity_kw: CapacityKW = Field(
        examples=[5000.0],
        description="Rated capacity in kilowatts",
    )
    uptime_percent: UptimePct = Field(
        default=100.0,
        examples=[98.5],
        description="Current uptime percentage (0–100)",
    )

    @field_validator("name")
    @classmethod
    def name_strip_and_validate(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Plant name cannot be blank or whitespace only")
        # Prevent common injection / special char abuse
        forbidden = set('<>"{}|\\^`')
        if any(c in forbidden for c in stripped):
            raise ValueError("Plant name contains forbidden characters")
        return stripped

    @field_validator("location")
    @classmethod
    def location_strip(cls, v: str) -> str:
        return v.strip()

    @model_validator(mode="after")
    def offline_uptime_check(self) -> "PlantCreate":
        """Offline plants shouldn't report > 0% uptime — warn via validation."""
        if self.status == "offline" and self.uptime_percent > 0:
            raise ValueError(
                "A plant with status 'offline' must have uptime_percent = 0.0"
            )
        return self


class PlantUpdate(BaseModel):
    """Request body for updating an existing plant (all fields optional)."""
    name: PlantName | None = None
    location: Location | None = None
    status: PlantStatus | None = None
    capacity_kw: CapacityKW | None = None
    uptime_percent: UptimePct | None = None

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Plant name cannot be blank")
        return v

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PlantUpdate":
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("At least one field must be provided for update")
        return self


class PlantResponse(BaseModel):
    """Plant record as returned to the client."""
    id: str
    name: str
    location: str
    status: PlantStatus
    capacity_kw: float
    uptime_percent: float
    owner_id: str
    created_at: datetime
    updated_at: datetime


class PlantQueryParams(BaseModel):
    """Query parameters for listing plants (validated as a dependency)."""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")
    status: PlantStatus | None = Field(default=None, description="Filter by status")
    min_uptime: float | None = Field(default=None, ge=0, le=100, description="Minimum uptime %")
