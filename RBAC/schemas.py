from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class OrganizationCreate(BaseModel):
    name: str

    class Config:
        from_attributes = True

class OrganizationRead(BaseModel):
    id: int
    name: str
    creation_date: datetime

    class Config:
        from_attributes = True

class TeamCreate(BaseModel):
    organization_id: int
    name: str

    class Config:
        from_attributes = True

class TeamRead(BaseModel):
    id: int
    organization_id: int
    name: str

    class Config:
        from_attributes = True

class OrganizationUserRead(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: str

    class Config:
        from_attributes = True

class TeamMemberRead(BaseModel):
    id: int
    team_id: int
    user_id: int

    class Config:
        from_attributes = True
