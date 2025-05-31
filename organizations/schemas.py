import re

from pydantic import BaseModel, model_validator, ConfigDict
from typing import Optional

from auth.schemas import UserRead
from roles.schemas import RoleRead


class OrganizationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    slug: Optional[str] = None

    @model_validator(mode='after')
    def generate_slug_from_name(self):
        """Auto-generate slug from name if not provided"""
        if not self.slug and self.name:
            slug = self.name.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[\s_]+', '-', slug)
            slug = re.sub(r'-+', '-', slug)
            slug = slug.strip('-')
            self.slug = slug

        return self


class OrganizationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = None
    description: Optional[str] = None


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    creation_date: int


class OrganizationUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization: OrganizationRead
    user: UserRead
    role: RoleRead


class AssignUserRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    user_email: str
    role_id: int
