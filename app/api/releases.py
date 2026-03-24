# ruff: noqa: B008

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Release
from app.schemas.release import ReleaseCreate, ReleaseRead, ReleaseUpdate
from app.security import (
    DELETE_ROLES,
    READ_ROLES,
    WRITE_ROLES,
    get_current_user,
)
from app.services.resource_access import get_project_for_roles, get_release_for_roles
from app.services.status_service import (
    RELEASE_STATUS_CATEGORY,
    get_status_by_code_and_category,
    validate_status_category,
)

router = APIRouter(prefix="/api/releases", tags=["releases"])


@router.get("", response_model=list[ReleaseRead])
async def get_releases(
    project_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(Release).options(
        selectinload(Release.project), selectinload(Release.status)
    )
    if project_id is not None:
        await get_project_for_roles(db, current_user, project_id, READ_ROLES)
        query = query.where(Release.id_project == project_id)
    else:
        from app.models import ProjectMember

        query = query.join(
            ProjectMember, ProjectMember.id_project == Release.id_project
        ).where(ProjectMember.id_user == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ReleaseRead, status_code=status.HTTP_201_CREATED)
async def create_release(
    release_data: ReleaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await get_project_for_roles(
        db,
        current_user,
        release_data.id_project,
        WRITE_ROLES,
    )

    status_planning = await get_status_by_code_and_category(
        db,
        "planning",
        RELEASE_STATUS_CATEGORY,
    )

    release = Release(
        id_project=release_data.id_project,
        id_status=status_planning.id,
        name=release_data.name,
        description=release_data.description,
    )
    db.add(release)
    await db.commit()
    await db.refresh(release, ["project", "status"])
    return release


@router.patch("/{release_id}", response_model=ReleaseRead)
async def update_release(
    release_id: int,
    release_data: ReleaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    release = await get_release_for_roles(
        db,
        current_user,
        release_id,
        WRITE_ROLES,
        selectinload(Release.project),
        selectinload(Release.status),
    )

    if release_data.name is not None:
        release.name = release_data.name
    if release_data.description is not None:
        release.description = release_data.description
    if release_data.id_status is not None:
        await validate_status_category(
            db,
            release_data.id_status,
            RELEASE_STATUS_CATEGORY,
        )
        release.id_status = release_data.id_status

    await db.commit()
    await db.refresh(release, ["status"])
    return release


@router.delete("/{release_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_release(
    release_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    release = await get_release_for_roles(
        db,
        current_user,
        release_id,
        DELETE_ROLES,
    )

    await db.delete(release)
    await db.commit()
