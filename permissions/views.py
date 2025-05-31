from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from permissions.services import PermissionService
from permissions.schemas import PermissionCreate, PermissionUpdate
from db.pg_connection import get_db
from utils.serializers import ResponseData
from utils.permission_middleware import refresh_permissions_cache, get_permissions_from_cache


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


async def get_permissions_by_role(
    role_id: int,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Get permissions assigned to a specific role"""
    result = await permission_service.get_permissions_by_role(role_id)
    return result


async def get_permissions_by_scope(
    scope: str,
    permission_service: PermissionService = Depends(get_permission_service)
):
    """Get permissions filtered by scope"""
    result = await permission_service.get_permissions_by_scope(scope)
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
    permission_data = permission.model_dump()
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


async def refresh_permissions_cache_endpoint():
    """Refresh the permissions cache from database"""
    try:
        await refresh_permissions_cache()
        return ResponseData(
            success=True,
            message="Permissions cache refreshed successfully"
        ).model_dump()
    except Exception as e:
        return ResponseData(
            success=False,
            message=f"Failed to refresh permissions cache: {str(e)}"
        ).model_dump()


async def get_cached_permissions_endpoint():
    """Get current cached permissions"""
    try:
        cached_permissions = get_permissions_from_cache()
        return ResponseData(
            success=True,
            message="Cached permissions retrieved successfully",
            data=cached_permissions
        ).model_dump()
    except Exception as e:
        return ResponseData(
            success=False,
            message=f"Failed to retrieve cached permissions: {str(e)}"
        ).model_dump() 