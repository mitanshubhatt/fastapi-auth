from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from RBAC.models import Organization, OrganizationUser, Role
from RBAC.schemas import OrganizationCreate, OrganizationRead
from auth.models import User
from utils.custom_logger import logger

async def create_organization_view(org: OrganizationCreate, db: AsyncSession, current_user: User):
    try:
        db_org = Organization(name=org.name)
        db.add(db_org)
        await db.commit()
        await db.refresh(db_org)

        admin_role = await db.execute(select(Role).where(Role.name == "Admin"))
        admin_role = admin_role.scalars().first()
        if not admin_role:
            raise HTTPException(status_code=500, detail="Admin role not found")

        org_user = OrganizationUser(
            organization_id=db_org.id, user_id=current_user.id, role_id=admin_role.id
        )
        db.add(org_user)
        await db.commit()
        await db.refresh(org_user)

        return OrganizationRead.from_orm(db_org)
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def assign_user_to_organization_view(user_email: str, organization_id: int, role_id: int, db: AsyncSession, current_user: User):
    try:
        org_user = await db.execute(
            select(OrganizationUser)
            .where(OrganizationUser.user_id == current_user.id, OrganizationUser.organization_id == organization_id)
        )
        org_user = org_user.scalars().first()
        if not org_user or org_user.role.name != "Admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")

        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        org_user = OrganizationUser(
            organization_id=organization_id, user_id=user.id, role_id=role_id
        )
        db.add(org_user)
        await db.commit()
        return {"message": "User assigned to organization successfully"}
    except Exception as e:
        logger.error(f"Error assigning user to organization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
