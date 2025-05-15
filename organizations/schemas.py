from pydantic import BaseModel

from RBAC.schemas import UserRead, RoleRead


class OrganizationCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True

class OrganizationRead(BaseModel):
    id: int
    name: str
    creation_date: int

    class Config:
        from_attributes = True

class OrganizationUserRead(BaseModel):
    id: int
    organization: OrganizationRead
    user: UserRead
    role: RoleRead

    class Config:
        from_attributes = True
