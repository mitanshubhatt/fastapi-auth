import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from organizations.models import OrganizationUser
from teams.models import TeamMember
from roles.models import Role
from permissions.models import RolePermission
from fastapi import HTTPException
from datetime import timedelta
from urllib.parse import urljoin
from html_templates.invite_template import invitation_template
from utils.email_provider import send_mail
from config.settings import settings
from utils.custom_logger import logger
from utils.serializers import ResponseData


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


async def send_invite_email(redis_client, email, organization_id, role_id, title):
    """
    Sends an email verification link to the specified email.

    Args:
        redis_client: Redis client for storing verification tokens.
        organization_id: organization id
        role_id: Role id
        title: Title of the mail
        email: User's email address.

    Raises:
        Exception: If there's an error sending the email.
    """
    try:
        # Generate a unique verification token
        verification_token = uuid.uuid4()
        token_key = f"{title}:{verification_token}"
        
        value = {
            "email": email,
            "organization_id": organization_id,
            "role_id": role_id
        }

        await redis_client.set(token_key, json.dumps(value), expire=timedelta(hours=24))

        invitation_url = urljoin(
            settings.hinata_host,
            f'auth/signup?inviteCode=${verification_token}'
        )
        invitation_link = f"https://{invitation_url}"

        subject = f"Registration Confirmation"
        body_html = invitation_template({
            "verifyLink": invitation_link
        })
        await send_mail(
            email=email,
            subject=subject,
            body_html=body_html
        )

        logger.info("Invitation email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send invitation email: {e}")
        raise e


async def add_user_to_organization(
    user_id: int, organization_id: int, role_id: int, db: AsyncSession
) -> ResponseData:
    """
    Add a user to an organization with a specific role.
    
    Args:
        user_id (int): The ID of the user to add.
        organization_id (int): The ID of the organization.
        role_id (int): The ID of the role to assign.
        db (AsyncSession): The database session.

    Returns:
        ResponseData: The response indicating success or failure.
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to add user to organization")
    try:
        # Check if the user is already part of the organization
        existing_user = await db.execute(
            select(OrganizationUser)
            .where(OrganizationUser.user_id == user_id, OrganizationUser.organization_id == organization_id)
        )
        existing_user = existing_user.scalars().first()
        if existing_user:
            response_data.message = "User is already part of the organization"
            return response_data

        org_user = OrganizationUser(
            organization_id=organization_id, user_id=user_id, role_id=role_id
        )
        db.add(org_user)
        await db.commit()

        response_data.success = True
        response_data.message = "User added to organization successfully"
        return response_data.model_dump()
    except Exception as e:
        logger.error(f"Error adding user to organization: {e}")
        response_data.message = "Internal server error"
        response_data.errors = [str(e)]
        return response_data.model_dump()
