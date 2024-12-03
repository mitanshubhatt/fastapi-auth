from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from RBAC.models import Team, TeamMember, OrganizationUser
from RBAC.schemas import TeamCreate, TeamRead
from auth.models import User
from utils.custom_logger import logger
from utils.serializers import ResponseData


async def create_team_view(team: TeamCreate, db: AsyncSession, current_user: User):
    """
    Create a team within an organization if the user has admin permissions.
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to create team")
    try:
        # Check if the user is an admin of the organization
        org_user = await db.execute(
            select(OrganizationUser).where(
                OrganizationUser.user_id == current_user.id,
                OrganizationUser.organization_id == team.organization_id,
            )
        )
        org_user = org_user.scalars().first()
        if not org_user or org_user.role.name != "Admin":
            response_data.message = "Not enough permissions"
            raise HTTPException(status_code=403, detail=response_data.dict())

        # Create the team
        db_team = Team(organization_id=team.organization_id, name=team.name)
        db.add(db_team)
        await db.commit()
        await db.refresh(db_team)

        response_data.success = True
        response_data.message = "Team created successfully"
        response_data.data = TeamRead.from_orm(db_team)
        return response_data.dict()
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())


async def assign_user_to_team_view(user_email: str, team_id: int, role_id: int, db: AsyncSession, current_user: User):
    """
    Assign a user to a team if the current user is a team admin.
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to assign user to team")
    try:
        # Ensure current user is a team admin
        team_member = await db.execute(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id,
                TeamMember.team_id == team_id,
            )
        )
        team_member = team_member.scalars().first()
        if not team_member or team_member.role.name != "Team Admin":
            response_data.message = "Not enough permissions"
            raise HTTPException(status_code=403, detail=response_data.dict())

        # Fetch the user by email
        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        if not user:
            response_data.message = "User not found"
            raise HTTPException(status_code=404, detail=response_data.dict())

        # Assign the user to the team
        new_team_member = TeamMember(team_id=team_id, user_id=user.id, role_id=role_id)
        db.add(new_team_member)
        await db.commit()

        response_data.success = True
        response_data.message = "User assigned to team successfully"
        return response_data.dict()
    except Exception as e:
        logger.error(f"Error assigning user to team: {e}")
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())


async def remove_user_from_team_view(user_email: str, team_id: int, db: AsyncSession, current_user: User):
    """
    Remove a user from a team.
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to remove user from team")
    try:
        # Fetch the user by email
        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        if not user:
            response_data.message = "User not found"
            raise HTTPException(status_code=404, detail=response_data.dict())

        # Check if the user is part of the team
        team_member = await db.execute(
            select(TeamMember)
            .where(TeamMember.user_id == user.id, TeamMember.team_id == team_id)
        )
        team_member = team_member.scalars().first()
        if not team_member:
            response_data.message = "User is not part of the team"
            raise HTTPException(status_code=404, detail=response_data.dict())

        # Remove the user from the team
        await db.delete(team_member)
        await db.commit()

        response_data.success = True
        response_data.message = f"User {user_email} successfully removed from team {team_id}"
        return response_data.dict()
    except Exception as e:
        logger.error(f"Error removing user from team: {e}")
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())
