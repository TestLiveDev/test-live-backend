from pydantic import BaseModel


class ReleaseTestCaseAssign(BaseModel):
    id_test_case: int


class ReleaseTestPlanAssign(BaseModel):
    id_test_plan: int
