# roles/views.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from roles.schemas import (
    RoleCreate, RoleRead, RoleUpdate
)
from roles.services import RoleService
from db.pg_connection import get_db
from auth.dependencies import get_current_user
from auth.models import User
from utils.serializers import ResponseData
from utils.custom_logger import logger


def get_role_service(
    db: AsyncSession = Depends(get_db)
) -> RoleService:
    return RoleService(db=db)


async def create_role(
    role: RoleCreate,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Create new role"""
    result = await role_service.create_new_role(role, current_user)
    return result


async def get_role_by_id(
    role_id: int,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Retrieve role by ID"""
    result = await role_service.retrieve_role_by_id(role_id, current_user)
    return result


async def get_role_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Retrieve role by slug"""
    result = await role_service.retrieve_role_by_slug(slug, current_user)
    return result


async def get_all_roles(
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Retrieve all roles"""
    result = await role_service.retrieve_all_roles(current_user)
    return result


async def update_role(
    role_id: int,
    role: RoleUpdate,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Update existing role"""
    role_data = role.model_dump(exclude_unset=True)
    result = await role_service.modify_role(role_id, role_data, current_user)
    return result


async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Delete role"""
    result = await role_service.remove_role(role_id, current_user)
    return result


async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Assign permission to role"""
    result = await role_service.assign_permission(role_id, permission_id, current_user)
    return result


async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Remove permission from role"""
    result = await role_service.remove_permission(role_id, permission_id, current_user)
    return result
