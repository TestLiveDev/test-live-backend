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
async def test_create_project(client):
    response = await client.post(
        "/api/projects",
        json={"name": "Project A", "description": "Main app"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Project A"


@pytest.mark.asyncio
async def test_get_projects(client):
    await client.post("/api/projects", json={"name": "Project A"})
    await client.post("/api/projects", json={"name": "Project B"})

    response = await client.get("/api/projects")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_create_project_assigns_owner_membership(client):
    response = await client.post("/api/projects", json={"name": "Project A"})
    project_id = response.json()["id"]

    members_response = await client.get(f"/api/projects/{project_id}/members")

    assert members_response.status_code == 200
    assert len(members_response.json()) == 1
    assert members_response.json()[0]["role"] == "owner"


@pytest.mark.asyncio
async def test_delete_project_conflict_when_has_releases(
    client, seed_status, seed_project
):
    await client.post(
        "/api/releases",
        json={"name": "Release 1.0", "id_project": seed_project.id},
    )

    response = await client.delete(f"/api/projects/{seed_project.id}")

    assert response.status_code == 409
