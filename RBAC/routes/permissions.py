from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import get_current_user
from db.connection import get_db
from RBAC.views.permissions import (
    create_permission_view,
    get_all_permissions_view,
    update_permission_view,
    assign_permission_to_role_view
)
from RBAC.schemas import PermissionCreate, PermissionUpdate
from auth.models import User

router = APIRouter(prefix="/rbac/permissions", tags=["Permissions"])

@router.post("/")
async def create_permission(
    permission: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_permission_view(permission, db, current_user)

@router.get("/")
async def get_all_permissions(db: AsyncSession = Depends(get_db)):
    return await get_all_permissions_view(db)

@router.put("/{permission_id}")
async def update_permission(
    permission_id: int,
    permission: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_permission_view(permission_id, permission, db, current_user)

@router.post("/assign-to-role")
async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await assign_permission_to_role_view(role_id, permission_id, db, current_user)
