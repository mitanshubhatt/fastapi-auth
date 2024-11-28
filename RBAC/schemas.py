from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrganizationCreate(BaseModel):
    name: str

    class Config:
        orm_mode = True
        from_attributes = True


class TeamCreate(BaseModel):
    name: str
    organization_id: int

    class Config:
        orm_mode = True
        from_attributes = True


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True


class OrganizationRead(BaseModel):
    id: int
    name: str
    creation_date: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class UserRead(BaseModel):
    id: int
    email: str
    full_name: Optional[str]

    class Config:
        orm_mode = True
        from_attributes = True


class OrganizationUserRead(BaseModel):
    id: int
    organization: OrganizationRead
    user: UserRead
    role: RoleRead

    class Config:
        orm_mode = True
        from_attributes = True


class TeamRead(BaseModel):
    id: int
    name: str
    organization: OrganizationRead

    class Config:
        orm_mode = True
        from_attributes = True


class TeamMemberRead(BaseModel):
    id: int
    team: TeamRead
    user: UserRead
    role: RoleRead

    class Config:
        orm_mode = True
        from_attributes = True
