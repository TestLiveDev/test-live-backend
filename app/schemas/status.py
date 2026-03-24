from pydantic import BaseModel, ConfigDict


class StatusBase(BaseModel):
    name: str
    code: str
    category: str


class StatusRead(StatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
