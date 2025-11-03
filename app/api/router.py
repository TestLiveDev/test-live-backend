from fastapi import APIRouter

from app.api.routes import organization
from app.api.routes import release


api_router = APIRouter()
api_router.include_router(organization.router)
api_router.include_router(release.router)
