from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from auth.models import User
from organizations.models import OrganizationUser
from teams.models import TeamMember, Team
from roles.models import Role
from permissions.models import Permission, RolePermission
from utils.custom_logger import logger


class ContextDAO:
    """Data Access Object for context-related database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            query = select(User).where(User.email == email)
            result = await self.db.execute(query)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None

    async def get_organization_context(self, user_email: str, organization_id: int) -> Optional[Dict[str, Any]]:
        """Get organization context for the user"""
        try:
            # First get the user
            user = await self.get_user_by_email(user_email)
            if not user:
                return None

            org_query = select(OrganizationUser).where(
                OrganizationUser.user_id == user.id,
                OrganizationUser.organization_id == organization_id
            ).options(
                selectinload(OrganizationUser.organization),
                selectinload(OrganizationUser.role)
            )
            
            result = await self.db.execute(org_query)
            org_user = result.scalars().first()
            
            if not org_user:
                return None
            
            return {
                "id": org_user.organization.id,
                "name": org_user.organization.name,
                "creation_date": org_user.organization.creation_date,
                "user_role": {
                    "id": org_user.role.id,
                    "name": org_user.role.name,
                    "slug": org_user.role.slug
                } if org_user.role else None
            }
            
        except Exception as e:
            logger.error(f"Error getting organization context: {str(e)}")
            return None

    async def get_team_context(self, user_email: str, team_id: int) -> Optional[Dict[str, Any]]:
        """Get team context for the user"""
        try:
            team_query = select(TeamMember).where(
                TeamMember.user_email == user_email,
                TeamMember.team_id == team_id
            ).options(
                selectinload(TeamMember.team),
                selectinload(TeamMember.role)
            )
            
            result = await self.db.execute(team_query)
            team_member = result.scalars().first()
            
            if not team_member:
                return None
            
            return {
                "id": team_member.team.id,
                "name": team_member.team.name,
                "description": team_member.team.description,
                "organization_id": team_member.team.organization_id,
                "user_role": {
                    "id": team_member.role.id,
                    "name": team_member.role.name,
                    "slug": team_member.role.slug
                } if team_member.role else None
            }
            
        except Exception as e:
            logger.error(f"Error getting team context: {str(e)}")
            return None

    async def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """Get team by ID"""
        try:
            query = select(Team).where(Team.id == team_id)
            result = await self.db.execute(query)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting team by id {team_id}: {str(e)}")
            return None

    async def get_organization_permissions(self, user_email: str, organization_id: int) -> List[str]:
        """Get permissions from organization role"""
        try:
            # Get user first
            user = await self.get_user_by_email(user_email)
            if not user:
                return []

            org_query = select(OrganizationUser).where(
                OrganizationUser.user_id == user.id,
                OrganizationUser.organization_id == organization_id
            ).options(selectinload(OrganizationUser.role))
            
            result = await self.db.execute(org_query)
            org_user = result.scalars().first()
            
            if not org_user or not org_user.role:
                return []
            
            return await self.get_role_permissions(org_user.role.id)
            
        except Exception as e:
            logger.error(f"Error getting organization permissions: {str(e)}")
            return []

    async def get_team_permissions(self, user_email: str, team_id: int) -> List[str]:
        """Get permissions from team role"""
        try:
            team_query = select(TeamMember).where(
                TeamMember.user_email == user_email,
                TeamMember.team_id == team_id
            ).options(selectinload(TeamMember.role))
            
            result = await self.db.execute(team_query)
            team_member = result.scalars().first()
            
            if not team_member or not team_member.role:
                return []
            
            return await self.get_role_permissions(team_member.role.id)
            
        except Exception as e:
            logger.error(f"Error getting team permissions: {str(e)}")
            return []

    async def get_role_permissions(self, role_id: int) -> List[str]:
        """Get all permissions for a role"""
        try:
            role_perm_query = select(RolePermission).where(
                RolePermission.role_id == role_id
            ).options(selectinload(RolePermission.permission))
            
            result = await self.db.execute(role_perm_query)
            role_permissions = result.scalars().all()
            
            return [rp.permission.slug for rp in role_permissions if rp.permission]
            
        except Exception as e:
            logger.error(f"Error getting role permissions: {str(e)}")
            return []

    async def get_user_organizations(self, user_email: str) -> List[Dict[str, Any]]:
        """Get all organizations for a user"""
        try:
            # Get user first
            user = await self.get_user_by_email(user_email)
            if not user:
                return []

            org_query = select(OrganizationUser).where(
                OrganizationUser.user_id == user.id
            ).options(selectinload(OrganizationUser.organization))
            
            result = await self.db.execute(org_query)
            org_users = result.scalars().all()
            
            return [
                {
                    "id": ou.organization.id,
                    "name": ou.organization.name
                }
                for ou in org_users
            ]
            
        except Exception as e:
            logger.error(f"Error getting user organizations: {str(e)}")
            return []

    async def get_user_teams(self, user_email: str, organization_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all teams for a user, optionally filtered by organization"""
        try:
            team_query = select(TeamMember).where(
                TeamMember.user_email == user_email
            ).options(selectinload(TeamMember.team))
            
            if organization_id:
                team_query = team_query.join(Team).where(Team.organization_id == organization_id)
            
            result = await self.db.execute(team_query)
            team_members = result.scalars().all()
            
            return [
                {
                    "id": tm.team.id,
                    "name": tm.team.name,
                    "organization_id": tm.team.organization_id
                }
                for tm in team_members
            ]
            
        except Exception as e:
            logger.error(f"Error getting user teams: {str(e)}")
            return []

    async def validate_user_organization_access(self, user_email: str, organization_id: int) -> bool:
        """Check if user has access to organization"""
        try:
            # Get user first
            user = await self.get_user_by_email(user_email)
            if not user:
                return False

            org_query = select(OrganizationUser).where(
                OrganizationUser.user_id == user.id,
                OrganizationUser.organization_id == organization_id
            )
            
            result = await self.db.execute(org_query)
            return result.scalars().first() is not None
            
        except Exception as e:
            logger.error(f"Error validating user organization access: {str(e)}")
            return False

    async def validate_user_team_access(self, user_email: str, team_id: int) -> bool:
        """Check if user has access to team"""
        try:
            team_query = select(TeamMember).where(
                TeamMember.user_email == user_email,
                TeamMember.team_id == team_id
            )
            
            result = await self.db.execute(team_query)
            return result.scalars().first() is not None
            
        except Exception as e:
            logger.error(f"Error validating user team access: {str(e)}")
            return False 