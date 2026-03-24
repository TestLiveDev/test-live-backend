from pydantic import BaseModel, ConfigDict


class TestStepRead(BaseModel):
    id: int
    id_test_case: int
    name: str
    expected_result: str | None = None
    order_num: int

    model_config = ConfigDict(from_attributes=True)
