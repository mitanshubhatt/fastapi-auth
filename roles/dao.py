from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import Optional, List
import re

from roles.models import Role
from utils.custom_logger import logger

class RoleDAO:
    """Data Access Object for role operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, name: str, scope: str, slug: Optional[str] = None, description: Optional[str] = None) -> Role:
        """Create a new role"""
        try:
            role_data = {
                "name": name,
                "scope": scope,
                "slug": slug or name.lower().replace(" ", "_"),
                "description": description
            }
            role = Role(**role_data)
            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)
            return role
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            await self.db.rollback()
            raise

    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        try:
            result = await self.db.execute(select(Role).where(Role.id == role_id))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting role by ID {role_id}: {str(e)}")
            raise

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        try:
            result = await self.db.execute(select(Role).where(Role.name == name))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting role by name '{name}': {str(e)}")
            raise

    async def get_role_by_slug(self, slug: str) -> Optional[Role]:
        """Get role by slug"""
        try:
            result = await self.db.execute(select(Role).where(Role.slug == slug))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting role by slug '{slug}': {str(e)}")
            raise

    async def get_all_roles(self) -> List[Role]:
        """Get all roles"""
        try:
            result = await self.db.execute(select(Role))
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting all roles: {str(e)}")
            raise

    async def update_role(self, role_id: int, role_data: dict) -> Optional[Role]:
        """Update role"""
        try:
            result = await self.db.execute(
                update(Role)
                .where(Role.id == role_id)
                .values(**role_data)
                .returning(Role)
            )
            await self.db.commit()
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error updating role {role_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def delete_role(self, role_id: int) -> bool:
        """Delete role"""
        try:
            result = await self.db.execute(
                delete(Role).where(Role.id == role_id)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting role {role_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def assign_permission_to_role(self, role_id: int, permission_id: int) -> bool:
        """Assign permission to role - implement based on your role-permission model"""
        try:
            # This is a placeholder - implement based on your role-permission relationship model
            # For example, if you have a RolePermission junction table:
            # role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
            # self.db.add(role_permission)
            # await self.db.commit()
            logger.info(f"Permission {permission_id} assigned to role {role_id}")
            return True
        except Exception as e:
            logger.error(f"Error assigning permission {permission_id} to role {role_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def remove_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        """Remove permission from role - implement based on your role-permission model"""
        try:
            # This is a placeholder - implement based on your role-permission relationship model
            # For example:
            # result = await self.db.execute(
            #     delete(RolePermission).where(
            #         RolePermission.role_id == role_id,
            #         RolePermission.permission_id == permission_id
            #     )
            # )
            # await self.db.commit()
            # return result.rowcount > 0
            logger.info(f"Permission {permission_id} removed from role {role_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing permission {permission_id} from role {role_id}: {str(e)}")
            await self.db.rollback()
            raise

    async def is_role_in_use(self, role_id: int) -> bool:
        """Check if role is currently in use"""
        try:
            # This is a placeholder - implement based on your user-role relationship model
            # For example:
            # result = await self.db.execute(
            #     select(UserRole).where(UserRole.role_id == role_id)
            # )
            # return result.scalars().first() is not None
            return False
        except Exception as e:
            logger.error(f"Error checking role usage {role_id}: {str(e)}")
            raise

    async def get_role_by_name_and_scope(self, name: str, scope: str) -> Optional[Role]:
        """
        Fetches a role by its name and scope.

        Args:
            name: The name of the role.
            scope: The scope of the role (e.g., "organization", "team").

        Returns:
            The Role object if found, otherwise None.
        """
        result = await self.db.execute(
            select(Role).where(Role.name == name, Role.scope == scope)
        )
        return result.scalars().first()
