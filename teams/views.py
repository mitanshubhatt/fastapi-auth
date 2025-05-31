from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from teams.schemas import TeamCreate, TeamUpdate, AssignUserToTeamRequest
from teams.services import TeamService
from auth.models import User
from db.pg_connection import get_db


def get_team_service(
    db: AsyncSession = Depends(get_db)
) -> TeamService:
    return TeamService(db=db)


async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Create a team within an organization"""
    result = await team_service.create_team(team_data, current_user)
    return result


async def get_team_by_id(
    team_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Get team by ID"""
    result = await team_service.get_team_by_id(team_id, current_user)
    return result


async def get_user_teams(
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Get all teams for current user"""
    result = await team_service.get_user_teams(current_user)
    return result


async def get_organization_teams(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Get all teams in an organization"""
    result = await team_service.get_organization_teams(organization_id, current_user)
    return result


async def get_team_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Get all members of a team"""
    result = await team_service.get_team_members(team_id, current_user)
    return result


async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Update team details"""
    team_dict = team_data.model_dump(exclude_unset=True)
    result = await team_service.update_team(team_id, team_dict, current_user)
    return result


async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Delete team"""
    result = await team_service.delete_team(team_id, current_user)
    return result


async def assign_user_to_team(
    team_id: int,
    request_data: AssignUserToTeamRequest,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Assign a user to a team"""
    result = await team_service.assign_user_to_team(
        user_email=str(request_data.user_email),
        team_id=team_id,
        role_id=request_data.role_id,
        current_user=current_user
    )
    return result


async def remove_user_from_team(
    team_id: int,
    user_email: str,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service)
):
    """Remove a user from a team"""
    result = await team_service.remove_user_from_team(
        user_email=user_email,
        team_id=team_id,
        current_user=current_user
    )
    return result 