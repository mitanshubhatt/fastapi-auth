import enum
from typing import Optional

from pydantic import BaseModel


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class RoleSlugEnum(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    LEAD = "lead"
    TEAM_MEMBER = "team_member"
    SUPER_ADMIN = "super_admin"
