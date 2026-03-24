# ruff: noqa: B008

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.test_result import TestResultCreate, TestResultRead, TestResultUpdate
from app.schemas.test_result_attachment import (
    TestResultAttachmentDownloadRead,
    TestResultAttachmentRead,
)
from app.security import DELETE_ROLES, READ_ROLES, WRITE_ROLES, get_current_user
from app.services.test_result_service import (
    create_or_update_result,
    delete_attachment,
    get_attachment_download,
    update_result_record,
    upload_attachment,
)

router = APIRouter(prefix="/api/results", tags=["results"])


@router.post("", response_model=TestResultRead, status_code=status.HTTP_201_CREATED)
async def create_result(
    result_data: TestResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await create_or_update_result(db, current_user, WRITE_ROLES, result_data)


@router.patch("/{result_id}", response_model=TestResultRead)
async def update_result(
    result_id: int,
    result_data: TestResultUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await update_result_record(
        db,
        current_user,
        result_id,
        WRITE_ROLES,
        result_data,
    )


@router.post(
    "/{result_id}/attachments",
    response_model=TestResultAttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_result_attachment(
    result_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await upload_attachment(db, current_user, result_id, WRITE_ROLES, file)


@router.get(
    "/{result_id}/attachments/{attachment_id}/download",
    response_model=TestResultAttachmentDownloadRead,
)
async def get_result_attachment_download_url(
    result_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_attachment_download(
        db,
        current_user,
        result_id,
        attachment_id,
        READ_ROLES,
    )


@router.delete(
    "/{result_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_result_attachment(
    result_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await delete_attachment(
        db,
        current_user,
        result_id,
        attachment_id,
        DELETE_ROLES,
    )
