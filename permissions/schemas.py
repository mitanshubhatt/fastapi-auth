from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    name: str
    description: str
    slug: str
    scope: str


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class PermissionUpdate(BaseModel):
    name: str = None
    description: str = None
    slug: str = None
    scope: str = None