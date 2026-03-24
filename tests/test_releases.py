import pytest
import pytest_asyncio

from app.models import Status


@pytest_asyncio.fixture
async def seed_status(db_session):
    status = Status(name="Планируется", code="planning", category="release_priority")
    db_session.add(status)
    await db_session.commit()
    return status


@pytest.mark.asyncio
async def test_create_release(client, seed_status, seed_project):
    response = await client.post(
        "/api/releases",
        json={
            "name": "Release 1.0",
            "description": "First release",
            "id_project": seed_project.id,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Release 1.0"
    assert data["description"] == "First release"
    assert data["id_project"] == seed_project.id
    assert data["id_status"] == seed_status.id
    assert "id" in data


@pytest.mark.asyncio
async def test_get_releases(client, seed_status, seed_project):
    await client.post(
        "/api/releases", json={"name": "Release 1.0", "id_project": seed_project.id}
    )
    await client.post(
        "/api/releases", json={"name": "Release 2.0", "id_project": seed_project.id}
    )

    response = await client.get("/api/releases")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_update_release(client, seed_status, seed_project):
    create_response = await client.post(
        "/api/releases",
        json={"name": "Release 1.0", "id_project": seed_project.id},
    )
    release_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/releases/{release_id}",
        json={"name": "Release 1.0 Updated"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Release 1.0 Updated"


@pytest.mark.asyncio
async def test_update_release_rejects_wrong_status_category(
    client, db_session, seed_status, seed_project
):
    result_status = Status(name="Пройден", code="passed", category="result")
    db_session.add(result_status)
    await db_session.commit()

    create_response = await client.post(
        "/api/releases",
        json={"name": "Release 1.0", "id_project": seed_project.id},
    )
    release_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/releases/{release_id}",
        json={"id_status": result_status.id},
    )

    assert response.status_code == 400
    assert "release_priority" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_release(client, seed_status, seed_project):
    create_response = await client.post(
        "/api/releases",
        json={"name": "Release 1.0", "id_project": seed_project.id},
    )
    release_id = create_response.json()["id"]

    response = await client.delete(f"/api/releases/{release_id}")

    assert response.status_code == 204
