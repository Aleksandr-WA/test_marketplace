from fastapi import APIRouter
from app.core.config import settings
from .parcels import router as users_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(
    users_router,
    prefix=settings.api.v1.parcels,
    tags=settings.api.v1.tag_parcels,
)
