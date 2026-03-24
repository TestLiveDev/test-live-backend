import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models import (
    Release,
    ReleaseTestCase,
    ReleaseTestPlan,
    Status,
    TestCase,
    TestPlan,
)


@pytest_asyncio.fixture
async def seed_for_results(db_session, seed_project):
    status = Status(name="Планируется", code="planning", category="release_priority")
    db_session.add(status)

    result_status = Status(name="Пройден", code="passed", category="result")
    db_session.add(result_status)

    priority = Status(name="Средний", code="medium", category="priority")
    db_session.add(priority)

    await db_session.commit()
    await db_session.refresh(result_status)

    release = Release(
        id_project=seed_project.id, id_status=status.id, name="Release 1.0"
    )
    db_session.add(release)
    await db_session.commit()

    test_plan = TestPlan(id_project=seed_project.id, name="Test Plan")
    db_session.add(test_plan)
    await db_session.commit()

    release_test_plan = ReleaseTestPlan(
        id_release=release.id,
        id_test_plan=test_plan.id,
    )
    db_session.add(release_test_plan)
    await db_session.commit()

    test_case = TestCase(
        id_test_plan=test_plan.id, id_priority=priority.id, name="Test Case"
    )
    db_session.add(test_case)
    await db_session.commit()

    release_test_case = ReleaseTestCase(
        id_release=release.id,
        id_test_case=test_case.id,
    )
    db_session.add(release_test_case)
    await db_session.commit()

    await db_session.refresh(test_case)
    await db_session.refresh(release)

    return {"release": release, "test_case": test_case, "result_status": result_status}


@pytest.mark.asyncio
async def test_create_result(client, seed_for_results):
    response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"]["code"] == "passed"


@pytest.mark.asyncio
async def test_update_existing_result(client, db_session, seed_for_results):
    await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )

    failed_status = Status(name="Провален", code="failed", category="result")
    db_session.add(failed_status)
    await db_session.commit()

    response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": failed_status.id,
        },
    )

    assert response.status_code == 201
    assert response.json()["status"]["code"] == "failed"


@pytest.mark.asyncio
async def test_update_result(client, seed_for_results):
    create_response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )
    result_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/results/{result_id}",
        json={"comment": "Fixed the issue"},
    )

    assert response.status_code == 200
    assert response.json()["comment"] == "Fixed the issue"


@pytest.mark.asyncio
async def test_create_result_rejects_unassigned_test_case(
    client, db_session, seed_for_results
):
    priority = await db_session.scalar(select(Status).where(Status.code == "medium"))
    extra_case = TestCase(
        id_test_plan=seed_for_results["test_case"].id_test_plan,
        id_priority=priority.id,
        name="Unassigned case",
    )
    db_session.add(extra_case)
    await db_session.commit()
    await db_session.refresh(extra_case)

    response = await client.post(
        "/api/results",
        json={
            "id_test_case": extra_case.id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Test case is not assigned to release"


@pytest.mark.asyncio
async def test_create_result_rejects_wrong_status_category(
    client, db_session, seed_for_results
):
    wrong_status = Status(
        name="Неверный статус результата",
        code="planning-extra",
        category="release_priority",
    )
    db_session.add(wrong_status)
    await db_session.commit()

    response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": wrong_status.id,
        },
    )

    assert response.status_code == 400
    assert "result" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_result_rejects_wrong_status_category(
    client, db_session, seed_for_results
):
    wrong_status = Status(
        name="Неверный статус результата 2",
        code="planning-update",
        category="release_priority",
    )
    db_session.add(wrong_status)
    await db_session.commit()

    create_response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )
    result_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/results/{result_id}",
        json={"id_status": wrong_status.id},
    )

    assert response.status_code == 400
    assert "result" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_result_statuses(client, seed_for_results):
    response = await client.get("/api/statuses?category=result")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["code"] == "passed"


@pytest.mark.asyncio
async def test_upload_result_attachment(client, monkeypatch, seed_for_results):
    create_response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )
    result_id = create_response.json()["id"]

    class UploadResult:
        etag = "etag-123"

    async def fake_upload_object(*args, **kwargs):
        return UploadResult()

    monkeypatch.setattr(
        "app.services.test_result_service.upload_object", fake_upload_object
    )

    response = await client.post(
        f"/api/results/{result_id}/attachments",
        files={"file": ("report.txt", b"execution log", "text/plain")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["original_name"] == "report.txt"
    assert data["content_type"] == "text/plain"
    assert data["size_bytes"] == len(b"execution log")


@pytest.mark.asyncio
async def test_attachment_is_exposed_in_release_scope(
    client, monkeypatch, seed_for_results
):
    create_response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )
    result_id = create_response.json()["id"]

    class UploadResult:
        etag = "etag-456"

    async def fake_upload_object(*args, **kwargs):
        return UploadResult()

    monkeypatch.setattr(
        "app.services.test_result_service.upload_object", fake_upload_object
    )

    upload_response = await client.post(
        f"/api/results/{result_id}/attachments",
        files={"file": ("screenshot.png", b"pngdata", "image/png")},
    )
    attachment_id = upload_response.json()["id"]

    scope_response = await client.get(
        f"/api/releases/{seed_for_results['release'].id}/scope"
    )

    assert scope_response.status_code == 200
    case_payload = scope_response.json()["plans"][0]["cases"][0]
    assert case_payload["result"]["attachments"][0]["id"] == attachment_id


@pytest.mark.asyncio
async def test_get_attachment_download_url(client, monkeypatch, seed_for_results):
    create_response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )
    result_id = create_response.json()["id"]

    class UploadResult:
        etag = "etag-789"

    async def fake_upload_object(*args, **kwargs):
        return UploadResult()

    async def fake_download_url(*args, **kwargs):
        return "http://minio.local/download"

    monkeypatch.setattr(
        "app.services.test_result_service.upload_object", fake_upload_object
    )
    monkeypatch.setattr(
        "app.services.test_result_service.get_presigned_download_url",
        fake_download_url,
    )

    upload_response = await client.post(
        f"/api/results/{result_id}/attachments",
        files={"file": ("evidence.log", b"log-data", "text/plain")},
    )
    attachment_id = upload_response.json()["id"]

    response = await client.get(
        f"/api/results/{result_id}/attachments/{attachment_id}/download"
    )

    assert response.status_code == 200
    assert response.json()["url"] == "http://minio.local/download"


@pytest.mark.asyncio
async def test_delete_attachment(client, monkeypatch, seed_for_results):
    create_response = await client.post(
        "/api/results",
        json={
            "id_test_case": seed_for_results["test_case"].id,
            "id_release": seed_for_results["release"].id,
            "id_status": seed_for_results["result_status"].id,
        },
    )
    result_id = create_response.json()["id"]

    class UploadResult:
        etag = "etag-111"

    deleted_keys = []

    async def fake_upload_object(*args, **kwargs):
        return UploadResult()

    async def fake_copy_object(*args, **kwargs):
        return None

    async def fake_remove_object(object_key, *args, **kwargs):
        deleted_keys.append(object_key)

    monkeypatch.setattr(
        "app.services.test_result_service.upload_object", fake_upload_object
    )
    monkeypatch.setattr(
        "app.services.object_storage_service.copy_object", fake_copy_object
    )
    monkeypatch.setattr(
        "app.services.object_storage_service.remove_object", fake_remove_object
    )

    upload_response = await client.post(
        f"/api/results/{result_id}/attachments",
        files={"file": ("artifact.txt", b"artifact", "text/plain")},
    )
    attachment_id = upload_response.json()["id"]

    response = await client.delete(
        f"/api/results/{result_id}/attachments/{attachment_id}"
    )

    assert response.status_code == 204
    assert len(deleted_keys) == 2
    assert any(key.startswith("project/") for key in deleted_keys)
    assert any(key.startswith("__trash__/") for key in deleted_keys)

    scope_response = await client.get(
        f"/api/releases/{seed_for_results['release'].id}/scope"
    )
    assert scope_response.status_code == 200
    case_payload = scope_response.json()["plans"][0]["cases"][0]
    assert case_payload["result"]["attachments"] == []
