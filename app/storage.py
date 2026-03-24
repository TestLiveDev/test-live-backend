from __future__ import annotations

from datetime import timedelta
from typing import BinaryIO, cast

from fastapi.concurrency import run_in_threadpool
from minio import Minio
from minio.commonconfig import CopySource

from app.config import settings


def get_minio_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
        region=settings.minio_region,
    )


async def ensure_minio_bucket(client: Minio | None = None) -> None:
    minio_client = client or get_minio_client()
    bucket_exists = await run_in_threadpool(
        minio_client.bucket_exists,
        settings.minio_bucket,
    )
    if not bucket_exists:
        if settings.minio_region:
            await run_in_threadpool(
                minio_client.make_bucket,
                settings.minio_bucket,
                settings.minio_region,
            )
        else:
            await run_in_threadpool(
                minio_client.make_bucket,
                settings.minio_bucket,
            )


async def upload_object(
    object_name: str,
    data: BinaryIO,
    length: int,
    content_type: str | None = None,
    metadata: dict[str, str | list[str] | tuple[str]] | None = None,
    client: Minio | None = None,
):
    minio_client = client or get_minio_client()
    await ensure_minio_bucket(minio_client)
    return await run_in_threadpool(
        lambda: minio_client.put_object(
            settings.minio_bucket,
            object_name,
            data,
            length,
            content_type=cast(str, content_type or "application/octet-stream"),
            metadata=metadata,
        )
    )


async def remove_object(object_name: str, client: Minio | None = None) -> None:
    minio_client = client or get_minio_client()
    await run_in_threadpool(
        minio_client.remove_object,
        settings.minio_bucket,
        object_name,
    )


async def copy_object(
    source_object_name: str,
    destination_object_name: str,
    client: Minio | None = None,
) -> None:
    minio_client = client or get_minio_client()
    await run_in_threadpool(
        minio_client.copy_object,
        settings.minio_bucket,
        destination_object_name,
        CopySource(settings.minio_bucket, source_object_name),
    )


async def get_presigned_download_url(
    object_name: str,
    client: Minio | None = None,
) -> str:
    minio_client = client or get_minio_client()
    return await run_in_threadpool(
        lambda: minio_client.get_presigned_url(
            "GET",
            settings.minio_bucket,
            object_name,
            expires=timedelta(seconds=settings.minio_presigned_expire_seconds),
        )
    )


async def remove_objects(
    object_names: list[str],
    client: Minio | None = None,
) -> None:
    for object_name in object_names:
        await remove_object(object_name, client)
