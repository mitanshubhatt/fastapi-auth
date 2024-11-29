from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from db.connection import get_db
from auth.dependencies import get_current_user
from views.teams import create_team_view, assign_user_to_team_view
from RBAC.schemas import TeamCreate, TeamRead

router = APIRouter(prefix="/rbac/teams", tags=["Teams"])

@router.post("/create", response_model=TeamRead)
async def create_team(
    team: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_team_view(team, db, current_user)

@router.post("/assign-user")
async def assign_user_to_team(
    user_email: str,
    team_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await assign_user_to_team_view(user_email, team_id, role_id, db, current_user)
