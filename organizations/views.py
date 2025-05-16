from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from db.pg_connection import get_db
from auth.dependencies import get_current_user, get_redis_client
from db.redis_connection import RedisClient

from organizations.services import OrganizationService
from organizations.schemas import OrganizationCreate
from utils.serializers import ResponseData


def get_organization_service(
    redis_client: RedisClient = Depends(get_redis_client),
    db: AsyncSession = Depends(get_db)
) -> OrganizationService:
    return OrganizationService(redis_client=redis_client, db=db)


async def create_organization(
    org: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    organization_service: OrganizationService = Depends(get_organization_service)
):
    created_org_data = await organization_service.create_organization(org, current_user)
    return ResponseData(success=True, message="Organization created successfully", data=created_org_data).dict()


async def assign_user_to_organization(
    user_email: str,
    organization_id: int,
    role_id: int,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    organization_service: OrganizationService = Depends(get_organization_service)
):
    result = await organization_service.assign_user_to_organization(
        user_email, organization_id, role_id, current_user, background_tasks
    )
    if "Invitation sent" in result.get("message", ""):
        return ResponseData(success=False, message=result["message"]).dict()
    return ResponseData(success=True, message=result["message"]).dict()