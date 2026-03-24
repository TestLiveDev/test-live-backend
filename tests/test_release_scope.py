import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models import (
    ProjectMember,
    ProjectRole,
    Release,
    ReleaseTestCase,
    ReleaseTestPlan,
    Status,
    TestCase,
    TestPlan,
    TestResult,
    TestStep,
    User,
)
from app.security import get_password_hash


@pytest_asyncio.fixture
async def seed_release_scope(db_session, seed_project):
    release_status = Status(
        name="Планируется",
        code="planning",
        category="release_priority",
    )
    passed_status = Status(name="Пройден", code="passed", category="result")
    failed_status = Status(name="Провален", code="failed", category="result")
    priority = Status(name="Средний", code="medium", category="priority")
    db_session.add_all([release_status, passed_status, failed_status, priority])
    await db_session.commit()

    release = Release(
        id_project=seed_project.id, id_status=release_status.id, name="Release 1.0"
    )
    smoke_plan = TestPlan(id_project=seed_project.id, name="Smoke")
    regression_plan = TestPlan(id_project=seed_project.id, name="Regression")
    db_session.add_all([release, smoke_plan, regression_plan])
    await db_session.commit()

    case_1 = TestCase(id_test_plan=smoke_plan.id, id_priority=priority.id, name="Login")
    case_2 = TestCase(
        id_test_plan=smoke_plan.id, id_priority=priority.id, name="Logout"
    )
    case_3 = TestCase(
        id_test_plan=regression_plan.id, id_priority=priority.id, name="Payments"
    )
    db_session.add_all([case_1, case_2, case_3])
    await db_session.commit()

    step_1 = TestStep(id_test_case=case_1.id, order_num=1, name="Open login page")
    step_2 = TestStep(id_test_case=case_1.id, order_num=2, name="Submit credentials")
    db_session.add_all([step_1, step_2])

    db_session.add_all(
        [
            ReleaseTestPlan(id_release=release.id, id_test_plan=smoke_plan.id),
            ReleaseTestPlan(id_release=release.id, id_test_plan=regression_plan.id),
            ReleaseTestCase(id_release=release.id, id_test_case=case_1.id),
            ReleaseTestCase(id_release=release.id, id_test_case=case_2.id),
            ReleaseTestCase(id_release=release.id, id_test_case=case_3.id),
        ]
    )
    db_session.add_all(
        [
            TestResult(
                id_release=release.id,
                id_test_case=case_1.id,
                id_status=passed_status.id,
                executed_by="qa.engineer",
            ),
            TestResult(
                id_release=release.id,
                id_test_case=case_3.id,
                id_status=failed_status.id,
                comment="Gateway issue",
            ),
        ]
    )
    await db_session.commit()

    return {"release": release}


@pytest.mark.asyncio
async def test_get_release_scope(client, seed_release_scope):
    response = await client.get(
        f"/api/releases/{seed_release_scope['release'].id}/scope"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["release"]["id"] == seed_release_scope["release"].id
    assert data["total_cases"] == 3
    assert data["passed"] == 1
    assert data["failed"] == 1
    assert data["not_run"] == 1
    assert len(data["plans"]) == 2
    assert data["plans"][0]["name"] == "Regression"
    assert data["plans"][1]["name"] == "Smoke"
    smoke_case = data["plans"][1]["cases"][0]
    assert smoke_case["name"] == "Login"
    assert len(smoke_case["steps"]) == 2
    assert smoke_case["result"]["status"]["code"] == "passed"


@pytest.mark.asyncio
async def test_get_release_scope_not_found(client):
    response = await client.get("/api/releases/999/scope")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_test_case_to_release(client, db_session, seed_release_scope):
    priority = await db_session.scalar(select(Status).where(Status.code == "medium"))
    smoke_plan = await db_session.scalar(
        select(TestPlan).where(TestPlan.name == "Smoke")
    )

    extra_case = TestCase(
        id_test_plan=smoke_plan.id,
        id_priority=priority.id,
        name="Password reset",
    )
    db_session.add(extra_case)
    await db_session.commit()
    await db_session.refresh(extra_case)

    response = await client.post(
        f"/api/releases/{seed_release_scope['release'].id}/test-cases",
        json={"id_test_case": extra_case.id},
    )

    assert response.status_code == 201
    data = response.json()
    smoke_plan_data = next(plan for plan in data["plans"] if plan["name"] == "Smoke")
    assert smoke_plan_data["total_cases"] == 3
    assert any(case["name"] == "Password reset" for case in smoke_plan_data["cases"])


@pytest.mark.asyncio
async def test_remove_test_case_from_release(client, db_session, seed_release_scope):
    regression_case = await db_session.scalar(
        select(TestCase).where(TestCase.name == "Payments")
    )

    response = await client.delete(
        f"/api/releases/{seed_release_scope['release'].id}/test-cases/{regression_case.id}"
    )

    assert response.status_code == 204

    scope_response = await client.get(
        f"/api/releases/{seed_release_scope['release'].id}/scope"
    )
    scope_data = scope_response.json()
    assert all(plan["name"] != "Regression" for plan in scope_data["plans"])

    removed_result = await db_session.scalar(
        select(TestResult).where(
            TestResult.id_release == seed_release_scope["release"].id,
            TestResult.id_test_case == regression_case.id,
        )
    )
    assert removed_result is None


@pytest.mark.asyncio
async def test_add_test_plan_to_release(client, db_session, seed_release_scope):
    priority = await db_session.scalar(select(Status).where(Status.code == "medium"))

    extra_plan = TestPlan(
        id_project=seed_release_scope["release"].id_project, name="Checkout"
    )
    db_session.add(extra_plan)
    await db_session.commit()
    await db_session.refresh(extra_plan)

    db_session.add_all(
        [
            TestCase(
                id_test_plan=extra_plan.id,
                id_priority=priority.id,
                name="Create order",
            ),
            TestCase(
                id_test_plan=extra_plan.id,
                id_priority=priority.id,
                name="Pay order",
            ),
        ]
    )
    await db_session.commit()

    response = await client.post(
        f"/api/releases/{seed_release_scope['release'].id}/test-plans",
        json={"id_test_plan": extra_plan.id},
    )

    assert response.status_code == 201
    data = response.json()
    checkout_plan = next(plan for plan in data["plans"] if plan["name"] == "Checkout")
    assert checkout_plan["total_cases"] == 2
    assert len(checkout_plan["cases"]) == 2


@pytest.mark.asyncio
async def test_remove_test_plan_from_release(client, db_session, seed_release_scope):
    smoke_plan = await db_session.scalar(
        select(TestPlan).where(TestPlan.name == "Smoke")
    )

    response = await client.delete(
        f"/api/releases/{seed_release_scope['release'].id}/test-plans/{smoke_plan.id}"
    )

    assert response.status_code == 204

    scope_response = await client.get(
        f"/api/releases/{seed_release_scope['release'].id}/scope"
    )
    scope_data = scope_response.json()
    assert all(plan["name"] != "Smoke" for plan in scope_data["plans"])

    remaining_cases = [case for plan in scope_data["plans"] for case in plan["cases"]]
    assert all(case["name"] not in {"Login", "Logout"} for case in remaining_cases)


@pytest.mark.asyncio
async def test_contributor_cannot_remove_test_case_from_release(
    db_session, client_for_user, seed_release_scope, seed_project
):
    contributor = User(
        email="contributor@example.com",
        password_hash=get_password_hash("password123"),
        full_name="Contributor User",
    )
    db_session.add(contributor)
    await db_session.commit()
    await db_session.refresh(contributor)

    db_session.add(
        ProjectMember(
            id_project=seed_project.id,
            id_user=contributor.id,
            role=ProjectRole.CONTRIBUTOR.value,
        )
    )
    await db_session.commit()

    regression_case = await db_session.scalar(
        select(TestCase).where(TestCase.name == "Payments")
    )

    async with await client_for_user(contributor) as client:
        response = await client.delete(
            f"/api/releases/{seed_release_scope['release'].id}/test-cases/{regression_case.id}"
        )

    assert response.status_code == 403
