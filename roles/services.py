from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Optional

from roles.dao import RoleDAO
from roles.schemas import RoleCreate
from roles.models import Role
from auth.models import User
from utils.custom_logger import logger
from utils.serializers import ResponseData
from utils.exceptions import (
    ConflictError, ValidationError, NotFoundError, DatabaseError, 
    InternalServerError, UnauthorizedError
)


class RoleService:
    """Facade service for role operations containing all business logic"""
    
    def __init__(self, db: AsyncSession):
        self.role_dao = RoleDAO(db=db)

    async def create_new_role(self, role_data: RoleCreate, current_user: User) -> dict:
        """Create a new role with comprehensive business logic and validation"""
        try:
            # Validate user permissions (basic check - can be enhanced)
            if not current_user:
                raise UnauthorizedError("Authentication required", "AUTH_REQUIRED")

            # Check for existing role by name
            existing_by_name = await self.role_dao.get_role_by_name(role_data.name)
            if existing_by_name:
                logger.warning(f"Role creation attempt with existing name: {role_data.name}")
                raise ConflictError(f"Role with name '{role_data.name}' already exists", "ROLE_NAME_EXISTS")

            # Check for existing role by slug if provided
            if role_data.slug:
                existing_by_slug = await self.role_dao.get_role_by_slug(role_data.slug)
                if existing_by_slug:
                    logger.warning(f"Role creation attempt with existing slug: {role_data.slug}")
                    raise ConflictError(f"Role with slug '{role_data.slug}' already exists", "ROLE_SLUG_EXISTS")

            # Create the role
            created_role = await self.role_dao.create_role(
                name=role_data.name,
                scope=role_data.scope,
                slug=role_data.slug,
                description=role_data.description
            )

            if not created_role:
                raise InternalServerError("Failed to create role", "ROLE_CREATION_FAILED")

            logger.info(f"Role '{created_role.name}' created successfully by user {current_user.email}")
            
            return ResponseData(
                success=True,
                message="Role created successfully",
                data={
                    "id": created_role.id,
                    "name": created_role.name,
                    "slug": created_role.slug,
                    "scope": created_role.scope,
                    "description": created_role.description
                }
            ).model_dump()

        except (ConflictError, UnauthorizedError, InternalServerError):
            raise
        except IntegrityError:
            logger.warning(f"Database integrity error during role creation for name '{role_data.name}'")
            raise ConflictError("A role with this name or slug already exists", "ROLE_ALREADY_EXISTS")
        except ValueError as ve:
            logger.error(f"Validation error during role creation: {ve}")
            raise ValidationError(str(ve), "ROLE_VALIDATION_ERROR")
        except Exception as e:
            logger.error(f"Unexpected error in role creation: {e}", exc_info=True)
            raise InternalServerError("An unexpected error occurred while creating the role", "ROLE_CREATION_ERROR")

    async def retrieve_role_by_id(self, role_id: int, current_user: User) -> dict:
        """Retrieve role by ID with business logic"""
        try:
            if not current_user:
                raise UnauthorizedError("Authentication required", "AUTH_REQUIRED")

            role = await self.role_dao.get_role_by_id(role_id)
            if not role:
                logger.warning(f"Role with ID {role_id} not found")
                raise NotFoundError(f"Role with ID {role_id} not found", "ROLE_NOT_FOUND")

            logger.info(f"Role {role.name} retrieved by user {current_user.email}")
            
            return ResponseData(
                success=True,
                message="Role retrieved successfully",
                data={
                    "id": role.id,
                    "name": role.name,
                    "slug": role.slug,
                    "scope": role.scope,
                    "description": role.description
                }
            ).model_dump()

        except (NotFoundError, UnauthorizedError):
            raise
        except Exception as e:
            logger.error(f"Error fetching role by ID {role_id}: {e}", exc_info=True)
            raise InternalServerError("Failed to retrieve role", "ROLE_FETCH_ERROR")

    async def retrieve_role_by_slug(self, slug: str, current_user: User) -> dict:
        """Retrieve role by slug with business logic"""
        try:
            if not current_user:
                raise UnauthorizedError("Authentication required", "AUTH_REQUIRED")

            role = await self.role_dao.get_role_by_slug(slug)
            if not role:
                logger.warning(f"Role with slug '{slug}' not found")
                raise NotFoundError(f"Role with slug '{slug}' not found", "ROLE_NOT_FOUND")

            logger.info(f"Role {role.name} retrieved by slug by user {current_user.email}")
            
            return ResponseData(
                success=True,
                message="Role retrieved successfully",
                data={
                    "id": role.id,
                    "name": role.name,
                    "slug": role.slug,
                    "scope": role.scope,
                    "description": role.description
                }
            ).model_dump()

        except (NotFoundError, UnauthorizedError):
            raise
        except Exception as e:
            logger.error(f"Error fetching role by slug '{slug}': {e}", exc_info=True)
            raise InternalServerError("Failed to retrieve role", "ROLE_FETCH_ERROR")

    async def retrieve_all_roles(self, current_user: User) -> dict:
        """Retrieve all roles with business logic"""
        try:
            if not current_user:
                raise UnauthorizedError("Authentication required", "AUTH_REQUIRED")

            roles = await self.role_dao.get_all_roles()
            logger.info(f"Retrieved {len(roles)} roles for user {current_user.email}")
            
            return ResponseData(
                success=True,
                message=f"Successfully retrieved {len(roles)} roles",
                data=[{
                    "id": role.id,
                    "name": role.name,
                    "slug": role.slug,
                    "scope": role.scope,
                    "description": role.description
                } for role in roles]
            ).model_dump()

        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving all roles: {e}", exc_info=True)
            raise InternalServerError("Failed to retrieve roles", "ROLES_FETCH_ERROR")

    async def modify_role(self, role_id: int, role_data: dict, current_user: User) -> dict:
        """Modify existing role with business logic and validation"""
        try:
            if not current_user:
                raise UnauthorizedError("Authentication required", "AUTH_REQUIRED")

            # Check if role exists
            existing_role = await self.role_dao.get_role_by_id(role_id)
            if not existing_role:
                logger.warning(f"Role update attempt for non-existent ID: {role_id}")
                raise NotFoundError(f"Role with ID {role_id} not found", "ROLE_NOT_FOUND")

            # Validate name uniqueness if name is being updated
            if "name" in role_data and role_data["name"] != existing_role.name:
                name_conflict = await self.role_dao.get_role_by_name(role_data["name"])
                if name_conflict and name_conflict.id != role_id:
                    logger.warning(f"Role name conflict during update: {role_data['name']}")
                    raise ConflictError(f"Role name '{role_data['name']}' already exists", "ROLE_NAME_EXISTS")

            # Validate slug uniqueness if slug is being updated
            if "slug" in role_data and role_data["slug"] != existing_role.slug:
                slug_conflict = await self.role_dao.get_role_by_slug(role_data["slug"])
                if slug_conflict and slug_conflict.id != role_id:
                    logger.warning(f"Role slug conflict during update: {role_data['slug']}")
                    raise ConflictError(f"Role slug '{role_data['slug']}' already exists", "ROLE_SLUG_EXISTS")

            # Update the role
            updated_role = await self.role_dao.update_role(role_id, role_data)
            if not updated_role:
                raise InternalServerError("Failed to update role", "ROLE_UPDATE_FAILED")

            logger.info(f"Role {updated_role.name} updated by user {current_user.email}")
            
            return ResponseData(
                success=True,
                message="Role updated successfully",
                data={
                    "id": updated_role.id,
                    "name": updated_role.name,
                    "slug": updated_role.slug,
                    "scope": updated_role.scope,
                    "description": updated_role.description
                }
            ).model_dump()

        except (NotFoundError, ConflictError, UnauthorizedError, InternalServerError):
            raise
        except Exception as e:
            logger.error(f"Error updating role {role_id}: {e}", exc_info=True)
            raise InternalServerError("Failed to update role", "ROLE_UPDATE_ERROR")

    async def remove_role(self, role_id: int, current_user: User) -> dict:
        """Remove role with business logic and validation"""
        try:
            if not current_user:
                raise UnauthorizedError("Authentication required", "AUTH_REQUIRED")

            # Check if role exists
            existing_role = await self.role_dao.get_role_by_id(role_id)
            if not existing_role:
                logger.warning(f"Role deletion attempt for non-existent ID: {role_id}")
                raise NotFoundError(f"Role with ID {role_id} not found", "ROLE_NOT_FOUND")

            # Check if role is being used (business logic)
            is_used = await self._check_role_usage(role_id)
            if is_used:
                logger.warning(f"Role deletion attempt for role in use: {existing_role.name}")
                raise ConflictError("Cannot delete role - it's currently assigned to users", "ROLE_IN_USE")

            # Delete the role
            success = await self.role_dao.delete_role(role_id)
            if not success:
                raise InternalServerError("Failed to delete role", "ROLE_DELETE_FAILED")

            logger.info(f"Role {existing_role.name} deleted by user {current_user.email}")
            
            return ResponseData(
                success=True,
                message=f"Role '{existing_role.name}' deleted successfully"
            ).model_dump()

        except (NotFoundError, ConflictError, UnauthorizedError, InternalServerError):
            raise
        except Exception as e:
            logger.error(f"Error deleting role {role_id}: {e}", exc_info=True)
            raise InternalServerError("Failed to delete role", "ROLE_DELETE_ERROR")

    async def assign_permission(self, role_id: int, permission_id: int, current_user: User) -> dict:
        """Assign permission to role with business logic"""
        try:
            if not current_user:
                raise UnauthorizedError("Authentication required", "AUTH_REQUIRED")

            # Validate role exists
            role = await self.role_dao.get_role_by_id(role_id)
            if not role:
                raise NotFoundError(f"Role with ID {role_id} not found", "ROLE_NOT_FOUND")

            # Assign permission (this would typically involve the permission service)
            success = await self.role_dao.assign_permission_to_role(role_id, permission_id)
            if not success:
                raise ConflictError("Permission is already assigned to this role", "PERMISSION_ALREADY_ASSIGNED")

            logger.info(f"Permission {permission_id} assigned to role {role.name} by user {current_user.email}")
            
            return ResponseData(
                success=True,
                message="Permission assigned to role successfully",
                data={
                    "role_id": role_id,
                    "permission_id": permission_id,
                    "role_name": role.name
                }
            ).model_dump()

        except (NotFoundError, ConflictError, UnauthorizedError):
            raise
        except Exception as e:
            logger.error(f"Error assigning permission {permission_id} to role {role_id}: {e}", exc_info=True)
            raise InternalServerError("Failed to assign permission to role", "PERMISSION_ASSIGNMENT_ERROR")

    async def remove_permission(self, role_id: int, permission_id: int, current_user: User) -> dict:
        """Remove permission from role with business logic"""
        try:
            if not current_user:
                raise UnauthorizedError("Authentication required", "AUTH_REQUIRED")

            # Validate role exists
            role = await self.role_dao.get_role_by_id(role_id)
            if not role:
                raise NotFoundError(f"Role with ID {role_id} not found", "ROLE_NOT_FOUND")

            # Remove permission
            success = await self.role_dao.remove_permission_from_role(role_id, permission_id)
            if not success:
                raise NotFoundError("Permission is not assigned to this role", "PERMISSION_NOT_ASSIGNED")

            logger.info(f"Permission {permission_id} removed from role {role.name} by user {current_user.email}")
            
            return ResponseData(
                success=True,
                message="Permission removed from role successfully",
                data={
                    "role_id": role_id,
                    "permission_id": permission_id,
                    "role_name": role.name
                }
            ).model_dump()

        except (NotFoundError, UnauthorizedError):
            raise
        except Exception as e:
            logger.error(f"Error removing permission {permission_id} from role {role_id}: {e}", exc_info=True)
            raise InternalServerError("Failed to remove permission from role", "PERMISSION_REMOVAL_ERROR")

    async def _check_role_usage(self, role_id: int) -> bool:
        """Check if role is currently being used by any users"""
        try:
            # This would check user_roles or similar table
            return await self.role_dao.is_role_in_use(role_id)
        except Exception as e:
            logger.warning(f"Could not check role usage: {str(e)}")
            # If we can't check, assume it's safe to delete
            return False


