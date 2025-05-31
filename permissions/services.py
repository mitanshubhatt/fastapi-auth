from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from permissions.dao import PermissionDAO
from permissions.models import Permission
from utils.custom_logger import logger
from utils.serializers import ResponseData
from utils.exceptions import (
    NotFoundError, ValidationError as CustomValidationError, ConflictError, 
    InternalServerError, DatabaseError
)


class PermissionService:
    """Facade service for permission operations containing all business logic"""
    
    def __init__(self, db: AsyncSession):
        self.permission_dao = PermissionDAO(db=db)

    async def retrieve_all_permissions(self) -> dict:
        """Retrieve all permissions with business logic"""
        try:
            permissions = await self.permission_dao.get_all_permissions()
            logger.info(f"Retrieved {len(permissions)} permissions")
            
            return ResponseData(
                success=True,
                message=f"Successfully retrieved {len(permissions)} permissions",
                data=[{
                    "id": perm.id,
                    "name": perm.name,
                    "description": perm.description,
                    "slug": perm.slug,
                    "scope": perm.scope
                } for perm in permissions]
            ).model_dump()
            
        except Exception as e:
            logger.error(f"Error retrieving permissions: {str(e)}")
            raise InternalServerError("Failed to retrieve permissions", "PERMISSIONS_RETRIEVAL_ERROR")

    async def retrieve_permission_by_id(self, permission_id: int) -> dict:
        """Retrieve permission by ID with business logic and validation"""
        try:
            permission = await self.permission_dao.get_permission_by_id(permission_id)
            if not permission:
                logger.warning(f"Permission with ID {permission_id} not found")
                raise NotFoundError(f"Permission with ID {permission_id} not found", "PERMISSION_NOT_FOUND")
            
            logger.info(f"Retrieved permission: {permission.name}")
            
            return ResponseData(
                success=True,
                message="Permission retrieved successfully",
                data={
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                    "slug": permission.slug,
                    "scope": permission.scope
                }
            ).model_dump()
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving permission {permission_id}: {str(e)}")
            raise InternalServerError("Failed to retrieve permission", "PERMISSION_RETRIEVAL_ERROR")

    async def retrieve_permission_by_name(self, name: str) -> dict:
        """Retrieve permission by name with business logic"""
        try:
            permission = await self.permission_dao.get_permission_by_name(name)
            if not permission:
                logger.info(f"Permission '{name}' not found")
                raise NotFoundError(f"Permission '{name}' not found", "PERMISSION_NOT_FOUND")
                
            logger.info(f"Found permission: {permission.name}")
            
            return ResponseData(
                success=True,
                message="Permission retrieved successfully",
                data={
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                    "slug": permission.slug,
                    "scope": permission.scope
                }
            ).model_dump()
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving permission by name '{name}': {str(e)}")
            raise InternalServerError("Failed to retrieve permission", "PERMISSION_RETRIEVAL_ERROR")

    async def create_new_permission(self, permission_data: dict) -> dict:
        """Create new permission with business logic and validation"""
        try:
            # Validate permission name uniqueness
            existing_permission = await self.permission_dao.get_permission_by_name(
                permission_data.get("name")
            )
            if existing_permission:
                logger.warning(f"Permission '{permission_data.get('name')}' already exists")
                raise ConflictError(f"Permission '{permission_data.get('name')}' already exists", "PERMISSION_EXISTS")

            # Create slug if not provided
            if "slug" not in permission_data or not permission_data["slug"]:
                permission_data["slug"] = permission_data["name"].lower().replace(" ", "_")

            # Validate required fields
            required_fields = ["name", "description", "scope"]
            for field in required_fields:
                if field not in permission_data or not permission_data[field]:
                    raise CustomValidationError(f"Field '{field}' is required", "MISSING_REQUIRED_FIELD")

            # Validate scope
            valid_scopes = ["organization", "team"]
            if permission_data["scope"] not in valid_scopes:
                raise CustomValidationError(
                    f"Scope must be one of: {', '.join(valid_scopes)}", 
                    "INVALID_SCOPE"
                )

            permission = await self.permission_dao.create_permission(permission_data)
            logger.info(f"Created new permission: {permission.name}")
            
            return ResponseData(
                success=True,
                message="Permission created successfully",
                data={
                    "id": permission.id,
                    "name": permission.name,
                    "description": permission.description,
                    "slug": permission.slug,
                    "scope": permission.scope
                }
            ).model_dump()
            
        except (ConflictError, CustomValidationError):
            raise
        except Exception as e:
            logger.error(f"Error creating permission: {str(e)}")
            raise InternalServerError("Failed to create permission", "PERMISSION_CREATION_ERROR")

    async def modify_permission(self, permission_id: int, permission_data: dict) -> dict:
        """Modify existing permission with business logic and validation"""
        try:
            # Check if permission exists
            existing_permission = await self.permission_dao.get_permission_by_id(permission_id)
            if not existing_permission:
                logger.warning(f"Permission with ID {permission_id} not found")
                raise NotFoundError(f"Permission with ID {permission_id} not found", "PERMISSION_NOT_FOUND")

            # Check name uniqueness if name is being updated
            if "name" in permission_data and permission_data["name"] != existing_permission.name:
                name_conflict = await self.permission_dao.get_permission_by_name(
                    permission_data["name"]
                )
                if name_conflict and name_conflict.id != permission_id:
                    logger.warning(f"Permission name '{permission_data['name']}' already exists")
                    raise ConflictError(f"Permission name '{permission_data['name']}' already exists", "PERMISSION_NAME_EXISTS")

            # Update slug if name is changed
            if "name" in permission_data and "slug" not in permission_data:
                permission_data["slug"] = permission_data["name"].lower().replace(" ", "_")

            # Validate scope if being updated
            if "scope" in permission_data:
                valid_scopes = ["organization", "team"]
                if permission_data["scope"] not in valid_scopes:
                    raise CustomValidationError(
                        f"Scope must be one of: {', '.join(valid_scopes)}", 
                        "INVALID_SCOPE"
                    )

            updated_permission = await self.permission_dao.update_permission(permission_id, permission_data)
            if not updated_permission:
                raise InternalServerError("Failed to update permission", "PERMISSION_UPDATE_FAILED")
                
            logger.info(f"Updated permission: {updated_permission.name}")
            
            return ResponseData(
                success=True,
                message="Permission updated successfully",
                data={
                    "id": updated_permission.id,
                    "name": updated_permission.name,
                    "description": updated_permission.description,
                    "slug": updated_permission.slug,
                    "scope": updated_permission.scope
                }
            ).model_dump()
            
        except (NotFoundError, ConflictError, CustomValidationError, InternalServerError):
            raise
        except Exception as e:
            logger.error(f"Error updating permission {permission_id}: {str(e)}")
            raise InternalServerError("Failed to update permission", "PERMISSION_UPDATE_ERROR")

    async def remove_permission(self, permission_id: int) -> dict:
        """Remove permission with business logic and validation"""
        try:
            # Check if permission exists
            existing_permission = await self.permission_dao.get_permission_by_id(permission_id)
            if not existing_permission:
                logger.warning(f"Permission with ID {permission_id} not found")
                raise NotFoundError(f"Permission with ID {permission_id} not found", "PERMISSION_NOT_FOUND")

            # Check if permission is being used (business logic)
            is_used = await self._check_permission_usage(permission_id)
            if is_used:
                logger.warning(f"Cannot delete permission {permission_id} - it's currently in use")
                raise ConflictError("Cannot delete permission - it's currently assigned to roles", "PERMISSION_IN_USE")

            success = await self.permission_dao.delete_permission(permission_id)
            if not success:
                raise InternalServerError("Failed to delete permission", "PERMISSION_DELETE_FAILED")
                
            logger.info(f"Deleted permission: {existing_permission.name}")
            
            return ResponseData(
                success=True,
                message=f"Permission '{existing_permission.name}' deleted successfully"
            ).model_dump()
                
        except (NotFoundError, ConflictError, InternalServerError):
            raise
        except Exception as e:
            logger.error(f"Error deleting permission {permission_id}: {str(e)}")
            raise InternalServerError("Failed to delete permission", "PERMISSION_DELETE_ERROR")

    async def assign_permission_to_role(self, role_id: int, permission_id: int) -> dict:
        """Assign permission to role with business logic"""
        try:
            # Validate permission exists
            permission = await self.permission_dao.get_permission_by_id(permission_id)
            if not permission:
                raise NotFoundError(f"Permission with ID {permission_id} not found", "PERMISSION_NOT_FOUND")

            # This would involve role validation - for now we'll assume role exists
            success = await self.permission_dao.assign_to_role(role_id, permission_id)
            if not success:
                raise ConflictError("Permission is already assigned to this role", "PERMISSION_ALREADY_ASSIGNED")
                
            logger.info(f"Assigned permission {permission.name} to role {role_id}")
            
            return ResponseData(
                success=True,
                message="Permission assigned to role successfully",
                data={
                    "role_id": role_id,
                    "permission_id": permission_id,
                    "permission_name": permission.name
                }
            ).model_dump()
                
        except (NotFoundError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Error assigning permission {permission_id} to role {role_id}: {str(e)}")
            raise InternalServerError("Failed to assign permission to role", "PERMISSION_ASSIGNMENT_ERROR")

    async def remove_permission_from_role(self, role_id: int, permission_id: int) -> dict:
        """Remove permission from role with business logic"""
        try:
            # Validate permission exists
            permission = await self.permission_dao.get_permission_by_id(permission_id)
            if not permission:
                raise NotFoundError(f"Permission with ID {permission_id} not found", "PERMISSION_NOT_FOUND")

            success = await self.permission_dao.remove_from_role(role_id, permission_id)
            if not success:
                raise NotFoundError("Permission is not assigned to this role", "PERMISSION_NOT_ASSIGNED")
                
            logger.info(f"Removed permission {permission.name} from role {role_id}")
            
            return ResponseData(
                success=True,
                message="Permission removed from role successfully",
                data={
                    "role_id": role_id,
                    "permission_id": permission_id,
                    "permission_name": permission.name
                }
            ).model_dump()
                
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error removing permission {permission_id} from role {role_id}: {str(e)}")
            raise InternalServerError("Failed to remove permission from role", "PERMISSION_REMOVAL_ERROR")

    async def _check_permission_usage(self, permission_id: int) -> bool:
        """Check if permission is currently being used by any roles"""
        try:
            return await self.permission_dao.is_permission_in_use(permission_id)
        except Exception as e:
            logger.warning(f"Could not check permission usage: {str(e)}")
            # If we can't check, assume it's safe to delete
            return False 