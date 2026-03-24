from pydantic import BaseModel

from app.schemas.release import ReleaseRead
from app.schemas.status import StatusRead
from app.schemas.test_result import TestResultRead
from app.schemas.test_step import TestStepRead


class ReleaseScopeCaseRead(BaseModel):
    id: int
    id_test_plan: int
    id_priority: int
    name: str
    description: str | None = None
    preconditions: str | None = None
    postconditions: str | None = None
    priority: StatusRead | None = None
    steps: list[TestStepRead]
    result: TestResultRead | None = None


class ReleaseScopePlanRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    total_cases: int
    passed: int
    failed: int
    blocked: int
    skipped: int
    not_run: int
    cases: list[ReleaseScopeCaseRead]


class ReleaseScopeRead(BaseModel):
    release: ReleaseRead
    total_cases: int
    passed: int
    failed: int
    blocked: int
    skipped: int
    not_run: int
    pass_rate: float
    plans: list[ReleaseScopePlanRead]
