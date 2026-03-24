# ruff: noqa: B008

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import ProjectMember, ProjectRole, User
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberRead,
    ProjectMemberRoleRead,
    ProjectMemberUpdate,
)
from app.security import (
    OWNER_ROLES,
    READ_ROLES,
    get_current_user,
    require_project_roles,
)

router = APIRouter(prefix="/api/projects", tags=["project-members"])


def _validate_role(role: str) -> None:
    allowed_roles = {item.value for item in ProjectRole}
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project role",
        )


def _to_member_read(member: ProjectMember) -> ProjectMemberRead:
    return ProjectMemberRead(
        id=member.id,
        id_project=member.id_project,
        id_user=member.id_user,
        role=member.role,
        created_at=member.created_at,
        updated_at=member.updated_at,
        email=member.user.email,
        full_name=member.user.full_name,
    )


@router.get("/{project_id}/members", response_model=list[ProjectMemberRead])
async def get_project_members(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await require_project_roles(db, current_user, project_id, READ_ROLES)
    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(ProjectMember.id_project == project_id)
    )
    return [_to_member_read(member) for member in result.scalars().all()]


@router.get("/{project_id}/members/me", response_model=ProjectMemberRoleRead)
async def get_my_project_role(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    membership = await require_project_roles(db, current_user, project_id, READ_ROLES)
    return ProjectMemberRoleRead(
        id_project=membership.id_project,
        id_user=membership.id_user,
        role=membership.role,
    )


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    project_id: int,
    member_data: ProjectMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await require_project_roles(db, current_user, project_id, OWNER_ROLES)
    _validate_role(member_data.role)

    user_result = await db.execute(
        select(User).where(User.email == member_data.email.lower())
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id_project == project_id,
            ProjectMember.id_user == user.id,
        )
    )
    existing_member = existing_result.scalar_one_or_none()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a project member",
        )

    member = ProjectMember(
        id_project=project_id, id_user=user.id, role=member_data.role
    )
    db.add(member)
    await db.commit()
    await db.refresh(member, ["user"])
    return _to_member_read(member)


@router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberRead)
async def update_project_member(
    project_id: int,
    user_id: int,
    member_data: ProjectMemberUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await require_project_roles(db, current_user, project_id, OWNER_ROLES)
    _validate_role(member_data.role)

    result = await db.execute(
        select(ProjectMember)
        .options(selectinload(ProjectMember.user))
        .where(
            ProjectMember.id_project == project_id,
            ProjectMember.id_user == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    if (
        member.id_user == current_user.id
        and member.role == ProjectRole.OWNER.value
        and member_data.role != ProjectRole.OWNER.value
    ):
        owners_result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.id_project == project_id,
                ProjectMember.role == ProjectRole.OWNER.value,
            )
        )
        owners = owners_result.scalars().all()
        if len(owners) == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project must have at least one owner",
            )

    member.role = member_data.role
    await db.commit()
    await db.refresh(member, ["user"])
    return _to_member_read(member)


@router.delete(
    "/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_project_member(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await require_project_roles(db, current_user, project_id, OWNER_ROLES)
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.id_project == project_id,
            ProjectMember.id_user == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    if member.role == ProjectRole.OWNER.value:
        owners_result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.id_project == project_id,
                ProjectMember.role == ProjectRole.OWNER.value,
            )
        )
        owners = owners_result.scalars().all()
        if len(owners) == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project must have at least one owner",
            )

    await db.delete(member)
    await db.commit()
