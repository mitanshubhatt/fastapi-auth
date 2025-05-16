from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import re

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

    async def create_role(self, name: str, scope: str, slug: Optional[str] = None, description: Optional[str] = None) -> \
    Optional[Role]:
        """
        Creates a new role in the database.
        If slug is not provided, it's generated from the name.
        Checks for uniqueness of name and slug.

        Args:
            name: The name for the new role (must be unique).
            scope: The scope for the new role (e.g., "organization", "team").
            slug: The slug for the new role (must be unique). If None, it will be auto-generated from the name.
            description: An optional description for the role.

        Returns:
            The created Role object if successful.
            Returns an existing Role object if a role with the same name or slug already exists.
            Returns None if slug generation fails or another error occurs.
        """
        try:
            # Generate slug from name if not provided
            if slug is None:
                s = name.lower()
                s = re.sub(r'[^\w\s-]', '', s)  # Remove non-alphanumeric, non-space, non-hyphen
                s = re.sub(r'\s+', '-', s)  # Replace whitespace with single hyphen
                s = s.strip('-')
                if not s:
                    logger.error(f"Could not generate a valid slug for name: '{name}'. A non-empty slug is required.")
                    return None  # Or raise a ValueError
                slug = s
                logger.info(f"Generated slug '{slug}' for role name '{name}'.")

            # Check if a role with the same name already exists
            existing_role_by_name = await self.get_role_by_slug(name)
            if existing_role_by_name:
                logger.warning(
                    f"Role with name '{name}' already exists (ID: {existing_role_by_name.id}). Returning existing role.")
                return existing_role_by_name

            # Check if a role with the same slug (provided or generated) already exists
            existing_role_by_slug = await self.get_role_by_slug(slug)
            if existing_role_by_slug:
                logger.warning(
                    f"Role with slug '{slug}' already exists (ID: {existing_role_by_slug.id}). Returning existing role.")
                return existing_role_by_slug

            new_role = Role(name=name, scope=scope, slug=slug, description=description)
            self.db.add(new_role)
            await self.db.commit()
            await self.db.refresh(new_role)
            logger.info(
                f"Role '{new_role.name}' (ID: {new_role.id}, Slug: {new_role.slug}) created successfully in scope '{new_role.scope}'.")
            return new_role
        except IntegrityError as ie:  # Catch errors from DB unique constraints
            await self.db.rollback()
            logger.error(f"Integrity error creating role with name '{name}', slug '{slug}': {ie}", exc_info=True)
            # Attempt to fetch again in case of race condition solved by DB constraint
            # This check ensures that if the error was due to a concurrent write, we return the now existing role
            existing_role = await self.get_role_by_slug(slug)
            if existing_role:
                logger.warning(
                    f"Returning existing role found after integrity error for name '{name}' or slug '{slug}'.")
                return existing_role
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating role with name '{name}', slug '{slug}': {e}", exc_info=True)
            return None

    async def get_role_by_slug(self, slug: str) -> Optional[Role]:
        """
        Fetches a role by its slug (assuming slug is globally unique).

        Args:
            slug: The slug of the role.

        Returns:
            The Role object if found, otherwise None.
        """
        try:
            result = await self.db.execute(select(Role).where(Role.slug == slug))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching role by slug '{slug}': {e}", exc_info=True)
            return None
