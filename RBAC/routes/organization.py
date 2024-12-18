from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User
from db.pg_connection import get_db
from auth.dependencies import get_current_user
from RBAC.views.organization import create_organization_view, assign_user_to_organization_view
from RBAC.schemas import OrganizationCreate
from auth.dependencies import get_redis_client
from db.redis_connection import RedisClient

router = APIRouter(prefix="/rbac/organizations", tags=["Organizations"])

@router.post("/create")
async def create_organization(
    org: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_organization_view(org, db, current_user)

@router.post("/assign-user")
async def assign_user_to_organization(
    user_email: str,
    organization_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await assign_user_to_organization_view(user_email, organization_id, role_id, db, current_user, redis_client)
