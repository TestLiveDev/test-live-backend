from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import ReleaseTestCase, TestCase, TestResult, TestResultAttachment, User
from app.schemas.test_result import TestResultCreate, TestResultUpdate
from app.schemas.test_result_attachment import TestResultAttachmentDownloadRead
from app.services.object_storage_service import (
    StagedObjectDeletion,
    commit_staged_object_deletions,
    rollback_staged_object_deletions,
    stage_object_deletions,
)
from app.services.resource_access import (
    get_release_for_roles,
    get_test_case_or_404,
    get_test_result_for_roles,
)
from app.services.status_service import (
    TEST_RESULT_STATUS_CATEGORY,
    validate_status_category,
)
from app.storage import get_presigned_download_url, remove_object, upload_object


def sanitize_file_name(file_name: str | None) -> str:
    candidate = Path(file_name or "attachment").name or "attachment"
    sanitized = "".join(
        character if character.isalnum() or character in {".", "_", "-"} else "_"
        for character in candidate
    ).strip("._")
    return sanitized[:120] or "attachment"


def build_attachment_object_key(test_result: TestResult, file_name: str) -> str:
    return (
        f"project/{test_result.release.id_project}/release/{test_result.id_release}"
        f"/result/{test_result.id}/{uuid4().hex}-{file_name}"
    )


async def get_attachment_or_404(
    db: AsyncSession,
    result_id: int,
    attachment_id: int,
) -> TestResultAttachment:
    result = await db.execute(
        select(TestResultAttachment).where(
            TestResultAttachment.id == attachment_id,
            TestResultAttachment.id_test_result == result_id,
        )
    )
    attachment = result.scalar_one_or_none()
    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )
    return attachment


async def create_or_update_result(
    db: AsyncSession,
    current_user: User,
    allowed_roles: set[str],
    result_data: TestResultCreate,
) -> TestResult:
    release = await get_release_for_roles(
        db,
        current_user,
        result_data.id_release,
        allowed_roles,
    )
    test_case = await get_test_case_or_404(
        db,
        result_data.id_test_case,
        selectinload(TestCase.test_plan),
    )
    if test_case.test_plan.id_project != release.id_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test case belongs to another project",
        )

    assignment_result = await db.execute(
        select(ReleaseTestCase).where(
            ReleaseTestCase.id_release == result_data.id_release,
            ReleaseTestCase.id_test_case == result_data.id_test_case,
        )
    )
    if assignment_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test case is not assigned to release",
        )

    await validate_status_category(
        db,
        result_data.id_status,
        TEST_RESULT_STATUS_CATEGORY,
    )

    existing = await db.execute(
        select(TestResult).where(
            and_(
                TestResult.id_test_case == result_data.id_test_case,
                TestResult.id_release == result_data.id_release,
            )
        )
    )
    existing_result = existing.scalar_one_or_none()

    if existing_result is not None:
        existing_result.id_status = result_data.id_status
        existing_result.comment = result_data.comment
        existing_result.executed_by = result_data.executed_by
        await db.commit()
        await db.refresh(existing_result, ["status", "attachments", "release"])
        return existing_result

    test_result = TestResult(**result_data.model_dump())
    db.add(test_result)
    await db.commit()
    await db.refresh(test_result, ["status", "attachments", "release"])
    return test_result


async def update_result_record(
    db: AsyncSession,
    current_user: User,
    result_id: int,
    allowed_roles: set[str],
    result_data: TestResultUpdate,
) -> TestResult:
    test_result = await get_test_result_for_roles(
        db,
        current_user,
        result_id,
        allowed_roles,
        selectinload(TestResult.status),
        selectinload(TestResult.release),
        selectinload(TestResult.attachments),
    )

    if result_data.id_status is not None:
        await validate_status_category(
            db,
            result_data.id_status,
            TEST_RESULT_STATUS_CATEGORY,
        )
        test_result.id_status = result_data.id_status
    if result_data.comment is not None:
        test_result.comment = result_data.comment
    if result_data.executed_by is not None:
        test_result.executed_by = result_data.executed_by

    await db.commit()
    await db.refresh(test_result, ["status", "attachments", "release"])
    return test_result


async def upload_attachment(
    db: AsyncSession,
    current_user: User,
    result_id: int,
    allowed_roles: set[str],
    file: UploadFile,
) -> TestResultAttachment:
    test_result = await get_test_result_for_roles(
        db,
        current_user,
        result_id,
        allowed_roles,
        selectinload(TestResult.release),
    )
    sanitized_name = sanitize_file_name(file.filename)

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )
    if file_size > settings.attachment_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is too large",
        )

    object_key = build_attachment_object_key(test_result, sanitized_name)
    upload_result = None
    try:
        upload_result = await upload_object(
            object_key,
            file.file,
            file_size,
            content_type=file.content_type,
            metadata={
                "original-name": sanitized_name,
                "result-id": str(test_result.id),
            },
        )
        attachment = TestResultAttachment(
            id_test_result=test_result.id,
            id_project=test_result.release.id_project,
            id_uploaded_by=current_user.id,
            bucket=settings.minio_bucket,
            object_key=object_key,
            original_name=sanitized_name,
            content_type=file.content_type,
            size_bytes=file_size,
            etag=upload_result.etag,
        )
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)
        return attachment
    except Exception:
        await db.rollback()
        if upload_result is not None:
            await remove_object(object_key)
        raise
    finally:
        await file.close()


async def get_attachment_download(
    db: AsyncSession,
    current_user: User,
    result_id: int,
    attachment_id: int,
    allowed_roles: set[str],
) -> TestResultAttachmentDownloadRead:
    await get_test_result_for_roles(
        db,
        current_user,
        result_id,
        allowed_roles,
        selectinload(TestResult.release),
    )
    attachment = await get_attachment_or_404(db, result_id, attachment_id)
    return TestResultAttachmentDownloadRead(
        url=await get_presigned_download_url(attachment.object_key),
        expires_in_seconds=settings.minio_presigned_expire_seconds,
    )


async def delete_attachment(
    db: AsyncSession,
    current_user: User,
    result_id: int,
    attachment_id: int,
    allowed_roles: set[str],
) -> None:
    await get_test_result_for_roles(
        db,
        current_user,
        result_id,
        allowed_roles,
        selectinload(TestResult.release),
    )
    attachment = await get_attachment_or_404(db, result_id, attachment_id)
    staged_deletions = await stage_object_deletions([attachment.object_key])

    try:
        await db.delete(attachment)
        await db.commit()
    except Exception:
        await db.rollback()
        await rollback_staged_object_deletions(staged_deletions)
        raise

    await commit_staged_object_deletions(staged_deletions)


def get_result_attachment_object_keys(test_results: list[TestResult]) -> list[str]:
    return [
        attachment.object_key
        for test_result in test_results
        for attachment in test_result.attachments
    ]


async def stage_result_attachment_deletions(
    test_results: list[TestResult],
) -> list[StagedObjectDeletion]:
    return await stage_object_deletions(get_result_attachment_object_keys(test_results))


async def delete_result_records(
    db: AsyncSession,
    test_results: list[TestResult],
) -> None:
    staged_deletions = await stage_result_attachment_deletions(test_results)

    try:
        for test_result in test_results:
            await db.delete(test_result)
        await db.commit()
    except Exception:
        await db.rollback()
        await rollback_staged_object_deletions(staged_deletions)
        raise

    await commit_staged_object_deletions(staged_deletions)
