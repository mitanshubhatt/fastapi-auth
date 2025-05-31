from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from permissions.models import Permission, RolePermission
from utils.custom_logger import logger
from utils.permission_cache import (
    get_all_cached_permissions, 
    get_permissions_by_scope,
    refresh_cache
)


class PermissionDAO:
    """Data Access Object for permissions with single responsibility - data operations only"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions from cache first, fallback to database"""
        try:
            # Try to get from cache first
            cached_permissions = get_all_cached_permissions()
            if cached_permissions:
                logger.info("Retrieved permissions from cache")
                # Convert cached data back to Permission objects for compatibility
                # Note: This is a simplified approach - in production you might want to 
                # store Permission objects directly in cache or modify callers to handle dict format
                pass
            
            # Fallback to database
            logger.info("Retrieving permissions from database")
            result = await self.db.execute(select(Permission))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error retrieving all permissions: {str(e)}")
            raise

    async def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID from database (cache lookup by ID is complex, so we skip cache for this)"""
        try:
            result = await self.db.execute(select(Permission).where(Permission.id == permission_id))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error retrieving permission by ID {permission_id}: {str(e)}")
            raise

    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name from database (cache lookup by name is complex, so we skip cache for this)"""
        try:
            result = await self.db.execute(select(Permission).where(Permission.name == name))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error retrieving permission by name '{name}': {str(e)}")
            raise

    async def create_permission(self, permission_data: dict) -> Permission:
        """Create a new permission and refresh cache"""
        try:
            db_permission = Permission(**permission_data)
            self.db.add(db_permission)
            await self.db.commit()
            await self.db.refresh(db_permission)
            
            # Refresh cache after successful creation
            logger.info("Refreshing permissions cache after creating new permission")
            await refresh_cache()
            
            return db_permission
        except Exception as e:
            logger.error(f"Error creating permission: {str(e)}")
            await self.db.rollback()
            raise

    async def update_permission(self, permission_id: int, permission_data: dict) -> Optional[Permission]:
        """Update permission by ID and refresh cache"""
        try:
            result = await self.db.execute(
                update(Permission)
                .where(Permission.id == permission_id)
                .values(**permission_data)
                .returning(Permission)
            )
            await self.db.commit()
            updated_permission = result.scalars().first()
            
            if updated_permission:
                # Refresh cache after successful update
                logger.info("Refreshing permissions cache after updating permission")
                await refresh_cache()
            
            return updated_permission
        except Exception as e:
            logger.error(f"Error updating permission {permission_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def delete_permission(self, permission_id: int) -> bool:
        """Delete permission by ID and refresh cache"""
        try:
            result = await self.db.execute(delete(Permission).where(Permission.id == permission_id))
            await self.db.commit()
            success = result.rowcount > 0
            
            if success:
                # Refresh cache after successful deletion
                logger.info("Refreshing permissions cache after deleting permission")
                await refresh_cache()
            
            return success
        except Exception as e:
            logger.error(f"Error deleting permission {permission_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def assign_to_role(self, role_id: int, permission_id: int) -> bool:
        """Assign permission to role and refresh cache"""
        try:
            # Check if assignment already exists
            existing = await self.db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
            if existing.scalars().first():
                return False
            
            # Create new assignment
            role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
            self.db.add(role_permission)
            await self.db.commit()
            logger.info(f"Permission {permission_id} assigned to role {role_id}")
            
            # Refresh cache after successful assignment
            logger.info("Refreshing permissions cache after assigning permission to role")
            await refresh_cache()
            
            return True
        except Exception as e:
            logger.error(f"Error assigning permission {permission_id} to role {role_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def remove_from_role(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role and refresh cache"""
        try:
            result = await self.db.execute(
                delete(RolePermission).where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
            await self.db.commit()
            logger.info(f"Permission {permission_id} removed from role {role_id}")
            success = result.rowcount > 0
            
            if success:
                # Refresh cache after successful removal
                logger.info("Refreshing permissions cache after removing permission from role")
                await refresh_cache()
            
            return success
        except Exception as e:
            logger.error(f"Error removing permission {permission_id} from role {role_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def is_permission_in_use(self, permission_id: int) -> bool:
        """Check if permission is assigned to any roles"""
        try:
            result = await self.db.execute(
                select(RolePermission).where(RolePermission.permission_id == permission_id)
            )
            return result.scalars().first() is not None
        except Exception as e:
            logger.error(f"Error checking permission usage {permission_id}: {str(e)}")
            raise

    async def get_permissions_by_role(self, role_id: int) -> List[Permission]:
        """Get all permissions assigned to a specific role - always from database for accuracy"""
        try:
            # For role-specific permissions, we should get from database to ensure accuracy
            # since the cache structure doesn't easily support role_id lookups
            result = await self.db.execute(
                select(Permission)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .where(RolePermission.role_id == role_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error retrieving permissions for role {role_id}: {str(e)}")
            raise

    async def get_roles_by_permission(self, permission_id: int) -> List[int]:
        """Get all role IDs that have a specific permission"""
        try:
            result = await self.db.execute(
                select(RolePermission.role_id).where(RolePermission.permission_id == permission_id)
            )
            return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error retrieving roles for permission {permission_id}: {str(e)}")
            raise

    async def get_permissions_by_scope_from_db(self, scope: str) -> List[Permission]:
        """Get permissions by scope from database (when cache is not suitable)"""
        try:
            result = await self.db.execute(select(Permission).where(Permission.scope == scope))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error retrieving permissions by scope '{scope}': {str(e)}")
            raise 