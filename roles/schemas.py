from typing import Optional

from pydantic import BaseModel


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True