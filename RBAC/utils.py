from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from RBAC.models import Role, RolePermission, OrganizationUser, TeamMember
from fastapi import HTTPException


async def has_permission(user_id: int, permission_name: str, scope: str, context_id: int, db: AsyncSession) -> bool:
    """
    Checks if a user has the given permission in the specified scope and context.
    :param user_id: ID of the user to check
    :param permission_name: Permission to check (e.g., "create_organization")
    :param scope: Scope of the permission ("organization" or "team")
    :param context_id: ID of the organization or team
    :param db: AsyncSession for database queries
    :return: Boolean indicating whether the user has the required permission
    """
    try:
        if scope == "organization":
            org_user = await db.execute(
                select(OrganizationUser)
                .join(Role)
                .where(OrganizationUser.user_id == user_id, OrganizationUser.organization_id == context_id)
            )
            org_user = org_user.scalars().first()
            if not org_user:
                raise HTTPException(status_code=403, detail="User not part of the organization")
            
            role_permissions = await db.execute(
                select(RolePermission)
                .join(Role)
                .where(Role.id == org_user.role_id, RolePermission.permission.has(name=permission_name))
            )
            return role_permissions.scalars().first() is not None

        elif scope == "team":
            team_member = await db.execute(
                select(TeamMember)
                .join(Role)
                .where(TeamMember.user_id == user_id, TeamMember.team_id == context_id)
            )
            team_member = team_member.scalars().first()
            if not team_member:
                raise HTTPException(status_code=403, detail="User not part of the team")
            
            role_permissions = await db.execute(
                select(RolePermission)
                .join(Role)
                .where(Role.id == team_member.role_id, RolePermission.permission.has(name=permission_name))
            )
            return role_permissions.scalars().first() is not None

        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Permission check failed: {e}")
