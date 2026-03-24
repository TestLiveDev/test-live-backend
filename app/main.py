import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import (
    auth,
    project_members,
    projects,
    release_scope,
    releases,
    statuses,
    test_cases,
    test_plans,
    test_results,
)
from app.storage import ensure_minio_bucket

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await ensure_minio_bucket()
    except Exception:
        logger.warning("MinIO bucket initialization skipped during startup")
    yield


app = FastAPI(
    title="TestLive API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(project_members.router)
app.include_router(projects.router)
app.include_router(releases.router)
app.include_router(release_scope.router)
app.include_router(statuses.router)
app.include_router(test_plans.router)
app.include_router(test_cases.router)
app.include_router(test_results.router)
