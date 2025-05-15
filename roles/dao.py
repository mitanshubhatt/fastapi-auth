from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List

from roles.models import Role
from utils.custom_logger import logger

class RoleDAO:
    def __init__(self, db: AsyncSession):
        """
        Initializes the RoleDAO with an asynchronous database session.

        Args:
            db: The AsyncSession for database operations.
        """
        self.db: AsyncSession = db

    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """
        Fetches a role by its ID.

        Args:
            role_id: The ID of the role to fetch.

        Returns:
            The Role object if found, otherwise None.
        """
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()

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