from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from permissions.models import Permission, RolePermission
from utils.custom_logger import logger


class PermissionDAO:
    """Data Access Object for permissions with single responsibility - data operations only"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions from database"""
        try:
            result = await self.db.execute(select(Permission))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error retrieving all permissions: {str(e)}")
            raise

    async def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        try:
            result = await self.db.execute(select(Permission).where(Permission.id == permission_id))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error retrieving permission by ID {permission_id}: {str(e)}")
            raise

    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name"""
        try:
            result = await self.db.execute(select(Permission).where(Permission.name == name))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error retrieving permission by name '{name}': {str(e)}")
            raise

    async def create_permission(self, permission_data: dict) -> Permission:
        """Create a new permission"""
        try:
            db_permission = Permission(**permission_data)
            self.db.add(db_permission)
            await self.db.commit()
            await self.db.refresh(db_permission)
            return db_permission
        except Exception as e:
            logger.error(f"Error creating permission: {str(e)}")
            await self.db.rollback()
            raise

    async def update_permission(self, permission_id: int, permission_data: dict) -> Optional[Permission]:
        """Update permission by ID"""
        try:
            result = await self.db.execute(
                update(Permission)
                .where(Permission.id == permission_id)
                .values(**permission_data)
                .returning(Permission)
            )
            await self.db.commit()
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error updating permission {permission_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def delete_permission(self, permission_id: int) -> bool:
        """Delete permission by ID"""
        try:
            result = await self.db.execute(delete(Permission).where(Permission.id == permission_id))
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting permission {permission_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def assign_to_role(self, role_id: int, permission_id: int) -> bool:
        """Assign permission to role"""
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
            return True
        except Exception as e:
            logger.error(f"Error assigning permission {permission_id} to role {role_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def remove_from_role(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role"""
        try:
            result = await self.db.execute(
                delete(RolePermission).where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
            await self.db.commit()
            logger.info(f"Permission {permission_id} removed from role {role_id}")
            return result.rowcount > 0
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
        """Get all permissions assigned to a specific role"""
        result = await self.db.execute(
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(RolePermission.role_id == role_id)
        )
        return result.scalars().all()

    async def get_roles_by_permission(self, permission_id: int) -> List[int]:
        """Get all role IDs that have a specific permission"""
        result = await self.db.execute(
            select(RolePermission.role_id).where(RolePermission.permission_id == permission_id)
        )
        return [row[0] for row in result.fetchall()] 