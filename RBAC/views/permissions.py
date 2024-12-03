from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from RBAC.models import Permission, RolePermission, Role
from RBAC.schemas import PermissionCreate, PermissionUpdate
from utils.custom_logger import logger

async def create_permission_view(permission: PermissionCreate, db: AsyncSession, current_user):
    """
    Create a new permission in the system.
    """
    try:
        existing_permission = await db.execute(
            select(Permission).where(Permission.name == permission.name)
        )
        if existing_permission.scalars().first():
            raise HTTPException(status_code=400, detail="Permission already exists")

        new_permission = Permission(name=permission.name, description=permission.description)
        db.add(new_permission)
        await db.commit()
        await db.refresh(new_permission)
        return {"message": "Permission created successfully", "permission": new_permission}
    except Exception as e:
        logger.error(f"Error creating permission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_all_permissions_view(db: AsyncSession):
    """
    Retrieve all permissions available in the system.
    """
    try:
        result = await db.execute(select(Permission))
        permissions = result.scalars().all()
        return [{"id": perm.id, "name": perm.name, "description": perm.description} for perm in permissions]
    except Exception as e:
        logger.error(f"Error retrieving permissions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_permission_view(permission_id: int, permission: PermissionUpdate, db: AsyncSession, current_user):
    """
    Update an existing permission.
    """
    try:
        db_permission = await db.execute(select(Permission).where(Permission.id == permission_id))
        db_permission = db_permission.scalars().first()

        if not db_permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        db_permission.name = permission.name
        db_permission.description = permission.description
        await db.commit()
        await db.refresh(db_permission)
        return {"message": "Permission updated successfully", "permission": db_permission}
    except Exception as e:
        logger.error(f"Error updating permission: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def assign_permission_to_role_view(role_id: int, permission_id: int, db: AsyncSession, current_user):
    """
    Assign a permission to a role.
    """
    try:
        role = await db.execute(select(Role).where(Role.id == role_id))
        role = role.scalars().first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        permission = await db.execute(select(Permission).where(Permission.id == permission_id))
        permission = permission.scalars().first()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        db.add(role_permission)
        await db.commit()
        return {"message": "Permission assigned to role successfully"}
    except Exception as e:
        logger.error(f"Error assigning permission to role: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
