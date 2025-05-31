import re

from pydantic import BaseModel, model_validator
from typing import Optional

from auth.schemas import UserRead
from roles.schemas import RoleRead


class OrganizationCreate(BaseModel):
    name: str
    slug: Optional[str] = None

    class Config:
        from_attributes = True

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
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class OrganizationRead(BaseModel):
    id: int
    name: str
    creation_date: int

    class Config:
        from_attributes = True


class OrganizationUserRead(BaseModel):
    id: int
    organization: OrganizationRead
    user: UserRead
    role: RoleRead

    class Config:
        from_attributes = True


class AssignUserRequest(BaseModel):
    user_email: str
    role_id: int

    class Config:
        from_attributes = True
