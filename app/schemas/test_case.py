from pydantic import BaseModel


class TestCaseCreate(BaseModel):
    id_test_plan: int
    name_test_case: str


class TestCaseDelete(BaseModel):
    id_test_case: int
