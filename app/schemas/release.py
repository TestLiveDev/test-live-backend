from .base import DBExecuteModel
from pydantic import BaseModel


class ReleaseDBQuery(DBExecuteModel):
    id_release: int
    id_organization: int
    name_release: str


class ReleaseCreate(BaseModel):
    id_organization: int
    name_release: str


class ReleaseUpdate(BaseModel):
    id_release: int
    name_release: str

class ReleaseDelete(BaseModel):
    id_release: int
