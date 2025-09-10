from fastapi import APIRouter

from app.api.routes import organization


api_router = APIRouter()
api_router.include_router(organization.router)
