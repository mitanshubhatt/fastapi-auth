from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from RBAC.models import Role, OrganizationUser, TeamMember
from utils.custom_logger import logger
from utils.serializers import ResponseData


async def get_roles_view(db: AsyncSession):
    """
    Retrieve all roles available in the system.
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to retrieve roles")
    try:
        result = await db.execute(select(Role))
        roles = result.scalars().all()
        response_data.success = True
        response_data.message = "Roles retrieved successfully"
        response_data.data = [
            {"id": role.id, "name": role.name, "description": role.description} for role in roles
        ]
        return response_data.dict()
    except Exception as e:
        logger.error(f"Error retrieving roles: {e}")
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())


async def get_user_role_in_organization_view(organization_id: int, db: AsyncSession, current_user):
    """
    Retrieve the current user's role in a specific organization.
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to retrieve user's role in organization")
    try:
        org_user = await db.execute(
            select(OrganizationUser).where(
                OrganizationUser.user_id == current_user.id,
                OrganizationUser.organization_id == organization_id,
            )
        )
        org_user = org_user.scalars().first()
        if not org_user:
            response_data.message = "Role not found"
            raise HTTPException(status_code=404, detail=response_data.dict())

        response_data.success = True
        response_data.message = "User role in organization retrieved successfully"
        response_data.data = {
            "organization_id": organization_id,
            "role_id": org_user.role.id,
            "role_name": org_user.role.name,
        }
        return response_data.dict()
    except Exception as e:
        logger.error(f"Error retrieving user's role in organization: {e}")
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())


async def get_user_role_in_team_view(team_id: int, db: AsyncSession, current_user):
    """
    Retrieve the current user's role in a specific team.
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to retrieve user's role in team")
    try:
        team_member = await db.execute(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id,
                TeamMember.team_id == team_id,
            )
        )
        team_member = team_member.scalars().first()
        if not team_member:
            response_data.message = "Role not found"
            raise HTTPException(status_code=404, detail=response_data.dict())

        response_data.success = True
        response_data.message = "User role in team retrieved successfully"
        response_data.data = {
            "team_id": team_id,
            "role_id": team_member.role.id,
            "role_name": team_member.role.name,
        }
        return response_data.dict()
    except Exception as e:
        logger.error(f"Error retrieving user's role in team: {e}")
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())
