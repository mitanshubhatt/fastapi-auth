from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from organizations.schemas import OrganizationRead
from roles.schemas import RoleRead
from auth.schemas import UserRead


class TeamCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    organization_id: int
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = None
    description: Optional[str] = None


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    organization: OrganizationRead


class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    team: TeamRead
    user: UserRead
    role: RoleRead


class AssignUserToTeamRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_email: EmailStr
    role_id: int