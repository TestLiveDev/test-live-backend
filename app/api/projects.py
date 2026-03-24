# ruff: noqa: B008

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Project, ProjectMember, ProjectRole
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.security import (
    OWNER_ROLES,
    get_current_user,
    require_project_roles,
)
from app.services.resource_access import get_project_or_404

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
async def get_projects(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(Project)
        .join(ProjectMember)
        .where(ProjectMember.id_user == current_user.id)
    )
    return result.scalars().all()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = Project(**project_data.model_dump())
    db.add(project)
    await db.flush()
    db.add(
        ProjectMember(
            id_project=project.id,
            id_user=current_user.id,
            role=ProjectRole.OWNER.value,
        )
    )
    await db.commit()
    await db.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = await get_project_or_404(db, project_id)
    await require_project_roles(db, current_user, project_id, OWNER_ROLES)

    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = await get_project_or_404(
        db,
        project_id,
        selectinload(Project.releases),
        selectinload(Project.test_plans),
    )
    await require_project_roles(db, current_user, project_id, OWNER_ROLES)

    if project.releases or project.test_plans:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project cannot be deleted while it has releases or test plans",
        )

    await db.delete(project)
    await db.commit()
