from typing import Optional

from pydantic import BaseModel

from organizations.schemas import OrganizationRead
from roles.schemas import RoleRead


class UserRead(BaseModel):
    id: int
    email: str
    full_name: Optional[str]

    class Config:
        from_attributes = True



class TeamCreate(BaseModel):
    name: str
    organization_id: int

    class Config:
        from_attributes = True


class TeamRead(BaseModel):
    id: int
    name: str
    organization: OrganizationRead

    class Config:
        from_attributes = True


class TeamMemberRead(BaseModel):
    id: int
    team: TeamRead
    user: UserRead
    role: RoleRead

    class Config:
        from_attributes = True