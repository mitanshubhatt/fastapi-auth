from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from db.pg_connection import get_db
from auth.dependencies import get_current_user
from RBAC.views.roles import get_roles_view, get_user_role_in_organization_view, get_user_role_in_team_view

router = APIRouter(prefix="/rbac/roles", tags=["Roles"])

@router.get("/")
async def get_roles(db: AsyncSession = Depends(get_db)):
    return await get_roles_view(db)

@router.get("/organization/{organization_id}")
async def get_current_user_role_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_user_role_in_organization_view(organization_id, db, current_user)

@router.get("/team/{team_id}")
async def get_current_user_role_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_user_role_in_team_view(team_id, db, current_user)
