import pytest
import pytest_asyncio

from app.models import Release, Status


@pytest_asyncio.fixture
async def seed_release(db_session, seed_project):
    status = Status(name="Планируется", code="planning", category="release_priority")
    db_session.add(status)
    await db_session.commit()

    release = Release(
        id_project=seed_project.id, id_status=status.id, name="Release 1.0"
    )
    db_session.add(release)
    await db_session.commit()
    await db_session.refresh(release)
    return release


@pytest.mark.asyncio
async def test_create_test_plan(client, seed_release):
    response = await client.post(
        "/api/test-plans",
        json={
            "name": "Test Plan 1",
            "description": "Desc",
            "id_project": seed_release.id_project,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Plan 1"
    assert data["description"] == "Desc"


@pytest.mark.asyncio
async def test_get_test_plans(client):
    project_response = await client.post("/api/projects", json={"name": "Project A"})
    project_id = project_response.json()["id"]
    await client.post(
        "/api/test-plans",
        json={"name": "Plan 1", "id_project": project_id},
    )
    await client.post(
        "/api/test-plans",
        json={"name": "Plan 2", "id_project": project_id},
    )

    response = await client.get("/api/test-plans")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_test_plan(client, seed_release):
    create_response = await client.post(
        "/api/test-plans",
        json={"name": "Original", "id_project": seed_release.id_project},
    )
    plan_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/test-plans/{plan_id}",
        json={"name": "Updated"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_test_plan(client, seed_release):
    create_response = await client.post(
        "/api/test-plans",
        json={"name": "To Delete", "id_project": seed_release.id_project},
    )
    plan_id = create_response.json()["id"]

    response = await client.delete(f"/api/test-plans/{plan_id}")

    assert response.status_code == 204
