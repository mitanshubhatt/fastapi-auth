from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class OrganizationCreate(BaseModel):
    name: str


class OrganizationRead(BaseModel):
    id: int
    name: str
    creation_date: datetime


class TeamCreate(BaseModel):
    organization_id: int
    product_id: int
    name: str


class TeamRead(BaseModel):
    id: int
    organization_id: int
    product_id: int
    name: str


class OrganizationUserRead(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: str


class TeamMemberRead(BaseModel):
    id: int
    team_id: int
    user_id: int