from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from organizations.dao import OrganizationDAO
from organizations.dao import UserDAO
from RBAC.schemas import OrganizationCreate, OrganizationRead #
from auth.models import User
from utils.custom_logger import logger
from db.redis_connection import RedisClient
from RBAC.utils import send_invite_email

class OrganizationService:
    def __init__(self, db: AsyncSession, redis_client: RedisClient):
        self.organization_dao = OrganizationDAO(db=db)
        self.user_dao = UserDAO(db=db)
        self.redis_client = redis_client

    async def create_organization(
        self, org_create_data: OrganizationCreate, current_user: User
    ) -> OrganizationRead:
        try:
            db_org = await self.organization_dao.create_organization(org_create_data)

            admin_role = await self.organization_dao.get_admin_role()
            if not admin_role:
                logger.error("Admin role not found during organization creation.")
                raise HTTPException(status_code=500, detail="Admin role not found")

            await self.organization_dao.add_user_to_organization(
                organization_id=db_org.id, user_id=current_user.id, role_id=admin_role.id
            )
            return OrganizationRead.model_validate(db_org)
        except Exception as e:
            logger.error(f"Error creating organization in service: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during organization creation")

    async def assign_user_to_organization(
        self,
        user_email: str,
        organization_id: int,
        role_id: int,
        current_user: User,
        background_tasks: BackgroundTasks,
    ):
        org_admin_membership = await self.organization_dao.get_organization_user(
            user_id=current_user.id, organization_id=organization_id
        )
        if not org_admin_membership or org_admin_membership.role.name != "Admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")

        target_user = await self.user_dao.get_user_by_email(user_email)

        if not target_user:
            background_tasks.add_task(
                send_invite_email,
                redis_client=self.redis_client,
                email=user_email,
                title="invitation_email",
                organization_id=organization_id,
                role_id=role_id,
            )
            return {"message": "User not found. Invitation sent."}

        existing_membership = await self.organization_dao.get_organization_user(
            user_id=target_user.id, organization_id=organization_id
        )
        if existing_membership:
             raise HTTPException(status_code=400, detail="User is already part of the organization")

        await self.organization_dao.add_user_to_organization(
            organization_id=organization_id, user_id=target_user.id, role_id=role_id
        )
        return {"message": "User added to organization successfully"}