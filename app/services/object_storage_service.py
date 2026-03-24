from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.storage import copy_object, remove_object


@dataclass(slots=True)
class StagedObjectDeletion:
    original_key: str
    staged_key: str


def build_staged_object_key(object_key: str) -> str:
    return f"__trash__/{uuid4().hex}/{Path(object_key).name}"


async def stage_object_deletions(object_keys: list[str]) -> list[StagedObjectDeletion]:
    staged_deletions: list[StagedObjectDeletion] = []

    try:
        for object_key in object_keys:
            staged_deletion = StagedObjectDeletion(
                original_key=object_key,
                staged_key=build_staged_object_key(object_key),
            )
            await copy_object(staged_deletion.original_key, staged_deletion.staged_key)
            await remove_object(staged_deletion.original_key)
            staged_deletions.append(staged_deletion)
    except Exception:
        await rollback_staged_object_deletions(staged_deletions)
        raise

    return staged_deletions


async def rollback_staged_object_deletions(
    staged_deletions: list[StagedObjectDeletion],
) -> None:
    for staged_deletion in reversed(staged_deletions):
        await copy_object(staged_deletion.staged_key, staged_deletion.original_key)
        await remove_object(staged_deletion.staged_key)


async def commit_staged_object_deletions(
    staged_deletions: list[StagedObjectDeletion],
) -> None:
    for staged_deletion in staged_deletions:
        await remove_object(staged_deletion.staged_key)
