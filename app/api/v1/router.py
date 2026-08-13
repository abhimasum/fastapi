"""
Aggregates all v1 API routers.

Add new endpoint modules here to register them with the app.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, plants

router = APIRouter(prefix="/api/v1")

# Register endpoint routers
router.include_router(auth.router)
router.include_router(plants.router)
