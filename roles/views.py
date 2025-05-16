# roles/views.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from roles.schemas import (
    RoleCreate, RoleRead
)
from roles.services import RoleService
from db.pg_connection import get_db
from auth.dependencies import get_current_user
from auth.models import User
from utils.serializers import ResponseData
from utils.custom_logger import logger


async def create_role(
        role_data: RoleCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Create a new role.
    Requires appropriate permissions (e.g., admin).
    """
    role_service = RoleService(db)
    response = ResponseData.model_construct(success=False,
                                            message="Failed to create role")  # Using generic ResponseData

    try:
        created_role = await role_service.create_role(role_data)
        response.success = True
        response.message = "Role created successfully"
        response.data = RoleRead.model_validate(created_role)
        return response.model_dump()
    except HTTPException as http_exc:
        logger.warning(f"HTTPException during role creation: {http_exc.status_code} - {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in create_role_view: {e}", exc_info=True)
        response.errors = [str(e)]
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.dict())


async def get_role_by_id(
        role_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific role by its ID.
    """
    role_service = RoleService(db)
    response = ResponseData.model_construct(success=False, message="Failed to fetch role")
    try:
        role = await role_service.get_role_by_id(role_id)
        response.success = True
        response.message = "Role fetched successfully"
        response.data = RoleRead.model_validate(role)
        return response.dict()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in get_role_by_id_view for ID {role_id}: {e}", exc_info=True)
        response.errors = [str(e)]
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.dict())


async def get_role_by_slug(
        slug: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific role by its slug.
    """
    role_service = RoleService(db)
    response = ResponseData.model_construct(success=False, message="Failed to fetch role by slug")
    try:
        role = await role_service.get_role_by_slug(slug)
        response.success = True
        response.message = "Role fetched successfully by slug"
        response.data = RoleRead.model_validate(role)
        return response.model_dump()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in get_role_by_slug_view for slug {slug}: {e}", exc_info=True)
        response.errors = [str(e)]
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.dict())
