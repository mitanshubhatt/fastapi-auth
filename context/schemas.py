from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SwitchOrganizationRequest(BaseModel):
    organization_id: int

    class Config:
        from_attributes = True


class SwitchTeamRequest(BaseModel):
    team_id: int

    class Config:
        from_attributes = True


class SwitchContextRequest(BaseModel):
    organization_id: Optional[int] = None
    team_id: Optional[int] = None

    class Config:
        from_attributes = True


class ContextInfo(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    user_role: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class OrganizationContext(ContextInfo):
    creation_date: Optional[int] = None

    class Config:
        from_attributes = True


class TeamContext(ContextInfo):
    description: Optional[str] = None
    organization_id: Optional[int] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    context: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class CurrentContextResponse(BaseModel):
    active_organization: Optional[OrganizationContext] = None
    active_team: Optional[TeamContext] = None
    permissions: Optional[List[str]] = None

    class Config:
        from_attributes = True


class AvailableContextsResponse(BaseModel):
    organizations: List[Dict[str, Any]]
    teams: List[Dict[str, Any]]

    class Config:
        from_attributes = True


class OrganizationInfo(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class TeamInfo(BaseModel):
    id: int
    name: str
    organization_id: int

    class Config:
        from_attributes = True 