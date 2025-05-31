from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from permissions.services import PermissionService
from permissions.schemas import PermissionCreate, PermissionUpdate
from db.pg_connection import get_db
from utils.serializers import ResponseData


def get_permission_service(
    db: AsyncSession = Depends(get_db)
) -> PermissionService:
    return PermissionService(db=db)


async def get_all_permissions(
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Retrieve all permissions"""
    result = await permission_service.retrieve_all_permissions()
    return result


async def get_permission_by_id(
    permission_id: int,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Retrieve permission by ID"""
    result = await permission_service.retrieve_permission_by_id(permission_id)
    return result


async def get_permission_by_name(
    name: str,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Retrieve permission by name"""
    result = await permission_service.retrieve_permission_by_name(name)
    return result


async def create_permission(
    permission: PermissionCreate,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Create new permission"""
    permission_data = permission.model_dump()
    result = await permission_service.create_new_permission(permission_data)
    return result


async def update_permission(
    permission_id: int,
    permission: PermissionUpdate,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Update existing permission"""
    permission_data = permission.model_dump(exclude_unset=True)
    result = await permission_service.modify_permission(permission_id, permission_data)
    return result


async def delete_permission(
    permission_id: int,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Delete permission"""
    result = await permission_service.remove_permission(permission_id)
    return result


async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Assign permission to role"""
    result = await permission_service.assign_permission_to_role(role_id, permission_id)
    return result


async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Remove permission from role"""
    result = await permission_service.remove_permission_from_role(role_id, permission_id)
    return result 