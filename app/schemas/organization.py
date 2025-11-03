from pydantic import BaseModel, ConfigDict


class OrganizationDBQuery(BaseModel):
    id_organization: int
    name_organization: str

    model_config = ConfigDict(
        from_attributes = True
    )


class OrganizationCreate(BaseModel):
    name_organization: str


class OrganizationUpdate(OrganizationCreate):
    id_organization: int


class OrganizationDelete(BaseModel):
    id_organization: int
