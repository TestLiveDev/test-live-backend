from fastapi import APIRouter

from app.api.routes import organization
from app.api.routes import release
from app.api.routes import test_plan

routes = (organization, release, test_plan)

api_router = APIRouter()
for rout in routes:
    api_router.include_router(rout.router)
