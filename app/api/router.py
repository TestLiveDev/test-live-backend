from fastapi import APIRouter

from app.api.routes import organization
from app.api.routes import release
from app.api.routes import test_plan
from app.api.routes import test_case

routes = (organization, release, test_plan, test_case)

api_router = APIRouter()
for rout in routes:
    api_router.include_router(rout.router)
