from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from context.dao import ContextDAO
from context.schemas import (
    CurrentContextResponse, AvailableContextsResponse,
    OrganizationContext, TeamContext
)
from utils.custom_logger import logger
from config.settings import settings


class ContextService:
    """Service layer for context switching operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.dao = ContextDAO(db)

    async def create_context_enriched_payload(
        self, 
        user_email: str,
        active_organization_id: Optional[int] = None,
        active_team_id: Optional[int] = None,
        custom_claims: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a JWT payload enriched with user's active context (current org/team)
        
        Args:
            user_email: User's email address
            active_organization_id: ID of the currently active organization
            active_team_id: ID of the currently active team
            custom_claims: Additional custom claims to include
            
        Returns:
            Dict containing the enriched payload data
        """
        try:
            # Get user basic info
            user = await self.dao.get_user_by_email(user_email)
            if not user:
                raise ValueError(f"User with email {user_email} not found")

            # Build base payload
            payload = {
                "sub": user_email,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "verified": user.verified,
                "auth_type": user.auth_type.value if user.auth_type else "local",
                "iat": datetime.utcnow().timestamp(),
            }

            # Add active organization context
            if active_organization_id:
                org_context = await self.dao.get_organization_context(user_email, active_organization_id)
                if org_context:
                    payload["active_organization"] = org_context

            # Add active team context
            if active_team_id:
                team_context = await self.dao.get_team_context(user_email, active_team_id)
                if team_context:
                    payload["active_team"] = team_context

            # Add context-specific permissions
            if active_organization_id or active_team_id:
                permissions = await self._get_context_permissions(
                    user_email, active_organization_id, active_team_id
                )
                payload["permissions"] = permissions

            # Add user's available organizations and teams (just IDs and names, not full data)
            user_orgs = await self.dao.get_user_organizations(user_email)
            user_teams = await self.dao.get_user_teams(user_email, active_organization_id)
            
            payload["available_organizations"] = user_orgs
            payload["available_teams"] = user_teams

            # Add custom claims
            if custom_claims:
                payload.update(custom_claims)

            logger.info(f"Created context-enriched payload for user {user_email}")
            return payload

        except Exception as e:
            logger.error(f"Error creating context-enriched payload for user {user_email}: {str(e)}")
            # Fall back to basic payload
            return {
                "sub": user_email,
                "email": user_email,
                "iat": datetime.utcnow().timestamp(),
            }

    async def _get_context_permissions(
        self, 
        user_email: str, 
        organization_id: Optional[int] = None, 
        team_id: Optional[int] = None
    ) -> List[str]:
        """Get permissions for the user in the current context"""
        permissions = set()
        
        try:
            # Get permissions from organization role
            if organization_id:
                org_perms = await self.dao.get_organization_permissions(user_email, organization_id)
                permissions.update(org_perms)
            
            # Get permissions from team role (may override or add to org permissions)
            if team_id:
                team_perms = await self.dao.get_team_permissions(user_email, team_id)
                permissions.update(team_perms)
            
            return list(permissions)
        
        except Exception as e:
            logger.error(f"Error getting context permissions: {str(e)}")
            return []

    async def validate_user_access_to_organization(self, user_email: str, organization_id: int) -> bool:
        """Validate if user has access to organization"""
        return await self.dao.validate_user_organization_access(user_email, organization_id)

    async def validate_user_access_to_team(self, user_email: str, team_id: int) -> bool:
        """Validate if user has access to team"""
        return await self.dao.validate_user_team_access(user_email, team_id)

    async def validate_team_belongs_to_organization(self, team_id: int, organization_id: int) -> bool:
        """Validate if team belongs to the specified organization"""
        try:
            team = await self.dao.get_team_by_id(team_id)
            return team is not None and team.organization_id == organization_id
        except Exception as e:
            logger.error(f"Error validating team organization: {str(e)}")
            return False

    async def get_current_context(self, token_payload: Dict[str, Any]) -> CurrentContextResponse:
        """Get current context from token payload"""
        try:
            active_org = token_payload.get("active_organization")
            active_team = token_payload.get("active_team")
            permissions = token_payload.get("permissions", [])

            org_context = None
            team_context = None

            if active_org:
                org_context = OrganizationContext(
                    id=active_org.get("id"),
                    name=active_org.get("name"),
                    creation_date=active_org.get("creation_date"),
                    user_role=active_org.get("user_role")
                )

            if active_team:
                team_context = TeamContext(
                    id=active_team.get("id"),
                    name=active_team.get("name"),
                    description=active_team.get("description"),
                    organization_id=active_team.get("organization_id"),
                    user_role=active_team.get("user_role")
                )

            return CurrentContextResponse(
                active_organization=org_context,
                active_team=team_context,
                permissions=permissions
            )

        except Exception as e:
            logger.error(f"Error getting current context: {str(e)}")
            return CurrentContextResponse()

    async def get_available_contexts(self, user_email: str) -> AvailableContextsResponse:
        """Get all available contexts for a user"""
        try:
            organizations = await self.dao.get_user_organizations(user_email)
            teams = await self.dao.get_user_teams(user_email)

            return AvailableContextsResponse(
                organizations=organizations,
                teams=teams
            )

        except Exception as e:
            logger.error(f"Error getting available contexts: {str(e)}")
            return AvailableContextsResponse(organizations=[], teams=[])

    async def create_new_token_with_context(
        self,
        user_email: str,
        organization_id: Optional[int] = None,
        team_id: Optional[int] = None
    ) -> str:
        """Create a new token with specified context"""
        try:
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
            
            new_token = await settings.auth_instance.create_context_enriched_token(
                user_email=user_email,
                db=self.db,
                expires_delta=expires_delta,
                active_organization_id=organization_id,
                active_team_id=team_id
            )
            
            return new_token
            
        except Exception as e:
            logger.error(f"Error creating new token with context: {str(e)}")
            raise


def extract_context_from_token(token_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract context information from token payload"""
    try:
        context = {}
        
        if "active_organization" in token_payload:
            context["active_organization"] = token_payload["active_organization"]
        
        if "active_team" in token_payload:
            context["active_team"] = token_payload["active_team"]
            
        if "permissions" in token_payload:
            context["permissions"] = token_payload["permissions"]
            
        if "available_organizations" in token_payload:
            context["available_organizations"] = token_payload["available_organizations"]
            
        if "available_teams" in token_payload:
            context["available_teams"] = token_payload["available_teams"]
        
        return context
    
    except Exception as e:
        logger.error(f"Error extracting context from token: {str(e)}")
        return {}


def check_permission_in_context(token_payload: Dict[str, Any], permission: str) -> bool:
    """Check if user has a specific permission in current context"""
    try:
        permissions = token_payload.get("permissions", [])
        return permission in permissions
    except Exception as e:
        logger.error(f"Error checking permission in context: {str(e)}")
        return False


def get_active_organization_id(token_payload: Dict[str, Any]) -> Optional[int]:
    """Get active organization ID from token payload"""
    active_org = token_payload.get("active_organization")
    return active_org.get("id") if active_org else None


def get_active_team_id(token_payload: Dict[str, Any]) -> Optional[int]:
    """Get active team ID from token payload"""
    active_team = token_payload.get("active_team")
    return active_team.get("id") if active_team else None 