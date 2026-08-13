"""
In-memory domain models — intentionally simple.
In production: replace with SQLAlchemy models + Alembic migrations.

The seeded users cover all three roles for testing.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from app.core.security import hash_password

# ── User ──────────────────────────────────────────────────────────────────────

Role = Literal["admin", "operator", "viewer"]


class UserInDB(BaseModel):
    """Internal user model — never exposed directly via API."""
    id: str
    username: str
    email: str
    hashed_password: str
    role: Role
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Plant ─────────────────────────────────────────────────────────────────────

PlantStatus = Literal["operational", "maintenance", "offline", "error"]


class PlantInDB(BaseModel):
    """Internal plant model."""
    id: str
    name: str
    location: str
    status: PlantStatus
    capacity_kw: float
    uptime_percent: float
    owner_id: str          # user ID who created it
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Seed Data ─────────────────────────────────────────────────────────────────

def _make_id() -> str:
    return str(uuid.uuid4())


def _seed_users() -> dict[str, UserInDB]:
    users = [
        UserInDB(id=_make_id(), username="admin", email="admin@bosch.example.com",
                 hashed_password=hash_password("Admin@123"), role="admin"),
        UserInDB(id=_make_id(), username="operator", email="operator@bosch.example.com",
                 hashed_password=hash_password("Operator@123"), role="operator"),
        UserInDB(id=_make_id(), username="viewer", email="viewer@bosch.example.com",
                 hashed_password=hash_password("Viewer@123"), role="viewer"),
    ]
    return {u.id: u for u in users}


USERS_DB: dict[str, UserInDB] = _seed_users()

# Username → user_id reverse index for login
USERNAME_INDEX: dict[str, str] = {u.username: u.id for u in USERS_DB.values()}

PLANTS_DB: dict[str, PlantInDB] = {}
