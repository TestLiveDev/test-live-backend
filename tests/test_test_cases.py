import pytest
import pytest_asyncio

from app.models import Release, Status, TestPlan


@pytest_asyncio.fixture
async def seed_test_plan(db_session, seed_project):
    status = Status(name="Планируется", code="planning", category="release_priority")
    db_session.add(status)

    priority = Status(name="Средний", code="medium", category="priority")
    db_session.add(priority)

    await db_session.commit()

    release = Release(
        id_project=seed_project.id, id_status=status.id, name="Release 1.0"
    )
    db_session.add(release)
    await db_session.commit()

    test_plan = TestPlan(id_project=seed_project.id, name="Test Plan")
    db_session.add(test_plan)
    await db_session.commit()
    await db_session.refresh(test_plan)
    return test_plan


@pytest.mark.asyncio
async def test_create_test_case(client, seed_test_plan):
    response = await client.post(
        "/api/test-cases",
        json={"name": "Test Case 1", "id_test_plan": seed_test_plan.id},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Case 1"
    assert data["id_test_plan"] == seed_test_plan.id
    assert data["priority"]["code"] == "medium"


@pytest.mark.asyncio
async def test_get_test_cases(client, seed_test_plan):
    await client.post(
        "/api/test-cases",
        json={"name": "Case 1", "id_test_plan": seed_test_plan.id},
    )
    await client.post(
        "/api/test-cases",
        json={"name": "Case 2", "id_test_plan": seed_test_plan.id},
    )

    response = await client.get("/api/test-cases")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_test_cases_by_plan(client, seed_test_plan):
    await client.post(
        "/api/test-cases",
        json={"name": "Case 1", "id_test_plan": seed_test_plan.id},
    )

    response = await client.get(f"/api/test-cases?test_plan_id={seed_test_plan.id}")

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_update_test_case(client, seed_test_plan):
    create_response = await client.post(
        "/api/test-cases",
        json={"name": "Original", "id_test_plan": seed_test_plan.id},
    )
    case_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/test-cases/{case_id}",
        json={"name": "Updated"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_create_test_case_rejects_wrong_status_category(
    client, db_session, seed_test_plan
):
    wrong_status = Status(
        name="Неверный приоритет",
        code="invalid-priority-create",
        category="release_priority",
    )
    db_session.add(wrong_status)
    await db_session.commit()

    response = await client.post(
        "/api/test-cases",
        json={
            "name": "Invalid Priority",
            "id_test_plan": seed_test_plan.id,
            "id_priority": wrong_status.id,
        },
    )

    assert response.status_code == 400
    assert "priority" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_test_case_rejects_wrong_status_category(
    client, db_session, seed_test_plan
):
    wrong_status = Status(
        name="Неверный приоритет 2",
        code="invalid-priority-update",
        category="release_priority",
    )
    db_session.add(wrong_status)
    await db_session.commit()

    create_response = await client.post(
        "/api/test-cases",
        json={"name": "Original", "id_test_plan": seed_test_plan.id},
    )
    case_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/test-cases/{case_id}",
        json={"id_priority": wrong_status.id},
    )

    assert response.status_code == 400
    assert "priority" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_test_case(client, seed_test_plan):
    create_response = await client.post(
        "/api/test-cases",
        json={"name": "To Delete", "id_test_plan": seed_test_plan.id},
    )
    case_id = create_response.json()["id"]

    response = await client.delete(f"/api/test-cases/{case_id}")

    assert response.status_code == 204
