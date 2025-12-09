from pydantic import BaseModel
from .base import DBExecuteModel


class TestPlanDBQuery(DBExecuteModel):
    id_test_plan: int
    id_organization: int
    id_parent: int | None
    name_test_plan: str
    id_test_case: int | None
    name_test_case: str | None
    lvl: int


class TestPlanCreate(BaseModel):
    id_organization: int
    id_parent: int | None
    name_test_plan: str


class TestPlanUpdate(BaseModel):
    id_test_plan: int
    name_test_plan: str


class TestPlanDelete(BaseModel):
    id_test_plan: int
