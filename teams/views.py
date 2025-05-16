# RBAC/views.py

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from teams.schemas import TeamCreate, TeamRead, AssignUserToTeamRequest # Added for clarity
from teams.services import TeamService
from auth.models import User
from db.pg_connection import get_db
from utils.serializers import ResponseData
from utils.custom_logger import logger




async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user), # Replace with your actual dependency
):
    """
    Create a team within an organization if the user has admin permissions.
    """
    team_service = TeamService(db)
    response_data = ResponseData.model_construct(success=False, message="Failed to create team")
    try:
        db_team = await team_service.create_team(team_data, current_user)
        response_data.success = True
        response_data.message = "Team created successfully"
        response_data.data = TeamRead.from_orm(db_team) # Or however TeamRead is populated
        return response_data.dict()
    except HTTPException as http_exc:
        # Re-raise HTTPExceptions raised by the service layer
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in create_team_view: {e}", exc_info=True)
        response_data.errors = [str(e)]
        # Return a generic 500 error if it's not an HTTPException
        raise HTTPException(status_code=500, detail=response_data.dict())


async def assign_user_to_team(
    team_id: int,
    request_data: AssignUserToTeamRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user), # Replace with your actual dependency
):
    """
    Assign a user to a team if the current user is a team admin.
    """
    team_service = TeamService(db)
    response_data = ResponseData.model_construct(success=False, message="Failed to assign user to team")
    try:
        await team_service.assign_user_to_team(
            user_email=str(request_data.user_email),
            team_id=team_id,
            role_id=request_data.role_id,
            current_user=current_user
        )
        response_data.success = True
        response_data.message = "User assigned to team successfully"
        return response_data.model_dump()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in assign_user_to_team_view: {e}", exc_info=True)
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.model_dump())


async def remove_user_from_team_view(
    team_id: int,
    user_email: str, # Could also be part of a request body or query param
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user), # Replace with your actual dependency
):
    """
    Remove a user from a team.
    """
    team_service = TeamService(db)
    response_data = ResponseData.model_construct(success=False, message="Failed to remove user from team")
    try:
        await team_service.remove_user_from_team(
            user_email=user_email,
            team_id=team_id,
            current_user=current_user # Pass current_user if service needs it for logging/permissions
        )
        response_data.success = True
        response_data.message = f"User {user_email} successfully removed from team {team_id}"
        return response_data.dict()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in remove_user_from_team_view: {e}", exc_info=True)
        response_data.errors = [str(e)]
        raise HTTPException(status_code=500, detail=response_data.dict())