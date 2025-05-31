from pydantic import BaseModel
from typing import Optional

from RBAC.schemas import UserRead, RoleRead


class OrganizationCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

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


class AssignUserRequest(BaseModel):
    user_email: str
    role_id: int

    class Config:
        from_attributes = True
