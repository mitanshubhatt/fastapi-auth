# roles/schemas.py

from pydantic import BaseModel, Field, validator, field_validator, ConfigDict
from typing import Optional, List
import re

from enum import Enum
class RoleScopeEnum(str, Enum):
    organization = "organization"
    team = "team"

class RoleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Name of the role")
    scope: str = Field(..., description="Scope of the role (e.g., 'organization', 'team')") # Consider using Enum for scope
    description: Optional[str] = Field(None, max_length=255, description="Description of the role")
    slug: Optional[str] = Field(None, min_length=3, max_length=50, description="URL-friendly slug. Auto-generated if not provided.")

    @validator('slug', always=True)
    def generate_slug_if_none(cls, v, values):
        if v is None and 'name' in values:
            name = values['name']
            s = name.lower()
            s = re.sub(r'[^\w\s-]', '', s)  # Remove non-alphanumeric, non-space, non-hyphen
            s = re.sub(r'\s+', '-', s)      # Replace whitespace with single hyphen
            v = s.strip('-')
            if not v: # Handle cases where name results in empty slug
                raise ValueError("Could not generate a valid slug from the provided name.")
        if v: # Validate slug format if provided or generated
            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
                raise ValueError("Slug must be lowercase alphanumeric with hyphens and no leading/trailing hyphens.")
        return v

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    scope: Optional[str] = Field(None) # Consider using Enum for scope
    description: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=50)

    @field_validator('slug')
    @classmethod
    def validate_slug_format(cls, v):
        if v is not None: # Only validate if slug is provided
            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
                raise ValueError("Slug must be lowercase alphanumeric with hyphens and no leading/trailing hyphens.")
        return v


class RoleRead(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    # permissions_cache: Optional[str] = None # If you want to expose this


