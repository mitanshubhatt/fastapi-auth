from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List

from organizations.models import Organization, OrganizationUser
from roles.models import Role
from organizations.schemas import OrganizationCreate
from auth.models import User

class OrganizationDAO:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_organization(self, org_data: OrganizationCreate) -> Organization:
        db_org = Organization(name=org_data.name)
        self.db.add(db_org)
        await self.db.commit()
        await self.db.refresh(db_org)
        return db_org

    async def get_organization_by_id(self, org_id: int) -> Optional[Organization]:
        result = await self.db.execute(select(Organization).where(Organization.id == org_id))
        return result.scalars().first()

    async def add_user_to_organization(
        self, organization_id: int, user_id: int, role_id: int
    ) -> OrganizationUser:
        org_user = OrganizationUser(
            organization_id=organization_id, user_id=user_id, role_id=role_id
        )
        self.db.add(org_user)
        await self.db.commit()
        await self.db.refresh(org_user)
        return org_user

    async def get_organization_user(
        self, user_id: int, organization_id: int
    ) -> Optional[OrganizationUser]:
        result = await self.db.execute(
            select(OrganizationUser)
            .options(selectinload(OrganizationUser.role))
            .where(OrganizationUser.user_id == user_id, OrganizationUser.organization_id == organization_id)
        )
        return result.scalars().first()

    async def get_user_organizations(self, user_id: int) -> List[OrganizationUser]:
        """Get all organizations for a user with organization and role details"""
        result = await self.db.execute(
            select(OrganizationUser)
            .options(
                selectinload(OrganizationUser.organization),
                selectinload(OrganizationUser.role),
                selectinload(OrganizationUser.user)
            )
            .where(OrganizationUser.user_id == user_id)
        )
        return result.scalars().all()

    async def get_organization_members(self, organization_id: int) -> List[OrganizationUser]:
        """Get all members of an organization with user and role details"""
        result = await self.db.execute(
            select(OrganizationUser)
            .options(
                selectinload(OrganizationUser.user),
                selectinload(OrganizationUser.role)
            )
            .where(OrganizationUser.organization_id == organization_id)
        )
        return result.scalars().all()

    async def get_admin_role(self) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.name == "Admin"))
        return result.scalars().first()
