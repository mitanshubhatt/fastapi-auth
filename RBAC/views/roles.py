from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from RBAC.models import Role, OrganizationUser, TeamMember
from utils.custom_logger import logger


async def get_roles_view(db: AsyncSession):
    """
    Retrieve all roles available in the system.
    """
    try:
        result = await db.execute(select(Role))
        roles = result.scalars().all()
        return [{"id": role.id, "name": role.name, "description": role.description} for role in roles]
    except Exception as e:
        logger.error(f"Error retrieving roles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_user_role_in_organization_view(organization_id: int, db: AsyncSession, current_user):
    """
    Retrieve the current user's role in a specific organization.
    """
    try:
        org_user = await db.execute(
            select(OrganizationUser).where(
                OrganizationUser.user_id == current_user.id,
                OrganizationUser.organization_id == organization_id,
            )
        )
        org_user = org_user.scalars().first()
        if not org_user:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"organization_id": organization_id, "role_id": org_user.role.id, "role_name": org_user.role.name}
    except Exception as e:
        logger.error(f"Error retrieving user's role in organization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_user_role_in_team_view(team_id: int, db: AsyncSession, current_user):
    """
    Retrieve the current user's role in a specific team.
    """
    try:
        team_member = await db.execute(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id,
                TeamMember.team_id == team_id,
            )
        )
        team_member = team_member.scalars().first()
        if not team_member:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"team_id": team_id, "role_id": team_member.role.id, "role_name": team_member.role.name}
    except Exception as e:
        logger.error(f"Error retrieving user's role in team: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
