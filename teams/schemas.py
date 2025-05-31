from typing import Optional

from pydantic import BaseModel, EmailStr

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
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TeamRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
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


class AssignUserToTeamRequest(BaseModel):
    user_email: EmailStr
    role_id: int

    class Config:
        from_attributes = True