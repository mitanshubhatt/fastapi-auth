from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from RBAC.models import Organization, OrganizationUser, Role
from RBAC.schemas import OrganizationCreate, OrganizationRead
from auth.models import User
from utils.custom_logger import logger
from utils.serializers import ResponseData
from db.redis_connection import RedisClient
from RBAC.utils import send_invite_email, add_user_to_organization

async def create_organization_view(org: OrganizationCreate, db: AsyncSession, current_user: User):
    """Create a new organization and assign the current user as an admin."""
    response_data = ResponseData.model_construct(success=False, message="Organization creation failed")
    try:
        db_org = Organization(name=org.name)
        db.add(db_org)
        await db.commit()
        await db.refresh(db_org)

        admin_role = await db.execute(select(Role).where(Role.name == "Admin"))
        admin_role = admin_role.scalars().first()
        if not admin_role:
            response_data.message = "Admin role not found"
            raise HTTPException(status_code=500, detail=response_data.dict())

        org_user = OrganizationUser(
            organization_id=db_org.id, user_id=current_user.id, role_id=admin_role.id
        )
        db.add(org_user)
        await db.commit()
        await db.refresh(org_user)

        response_data.success = True
        response_data.message = "Organization created successfully"
        response_data.data = OrganizationRead.from_orm(db_org)
        return response_data.dict()

    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        response_data.message = "Internal server error"
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())


async def assign_user_to_organization_view(
    user_email: str,
    organization_id: int,
    role_id: int,
    db: AsyncSession,
    current_user: User,
    background_tasks: BackgroundTasks,
    redis_client: RedisClient,
):
    """Assign a user to an organization with a specified role."""
    response_data = ResponseData.model_construct(success=False, message="Failed to assign user to organization")
    try:
        # Check if the current user has admin permissions
        org_user = await db.execute(
            select(OrganizationUser)
            .where(OrganizationUser.user_id == current_user.id, OrganizationUser.organization_id == organization_id)
        )
        org_user = org_user.scalars().first()
        if not org_user or org_user.role.name != "Admin":
            response_data.message = "Not enough permissions"
            raise HTTPException(status_code=403, detail=response_data.dict())

        # Check if the user exists
        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        if not user:
            response_data.success = False
            background_tasks.add_task(
                send_invite_email,
                redis_client=redis_client,
                email=user_email,
                title="invitation_email",
                organization_id=organization_id,
                role_id=role_id,
            )
            response_data.message = "User not found. Invitation sent."
            return response_data.dict()

        return await add_user_to_organization(user.id, organization_id, role_id, db)

    except Exception as e:
        logger.error(f"Error assigning user to organization: {e}")
        response_data.message = "Internal server error"
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())

