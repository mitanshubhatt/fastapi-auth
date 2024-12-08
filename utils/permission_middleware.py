from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth.dependencies import get_current_user
from RBAC.models import OrganizationUser, TeamMember
from utils.custom_logger import logger
from config.settings import settings

from collections import defaultdict

from sqlalchemy.orm import Session
from RBAC.models import Role, RolePermission
from db.pg_connection import get_db

def get_effective_permissions(role: str, scope: str) -> dict:
    """
    Get the effective permissions for a role, including inherited permissions.
    Handles wildcard routes for roles like Admin or Super Admin.
    """

    permissions = {}
    current_role = role

    while current_role:
        role_data = settings.permissions.get(scope, {}).get(current_role)
        if role_data:
            # Check for wildcard permissions
            if "*" in role_data["routes"]:
                # Add wildcard routes with all HTTP methods
                permissions["*"] = set(role_data["routes"]["*"])
            
            # Merge current role's permissions for specific routes
            for route, methods in role_data["routes"].items():
                if route != "*":  # Skip wildcard during normal route addition
                    permissions.setdefault(route, set()).update(methods)
            
            # Move to inherited role
            current_role = role_data["inherits"]
        else:
            break

    # Convert sets to lists for final output
    return {route: list(methods) for route, methods in permissions.items()}



class PermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "/auth" or "/docs" in request.url.path:
                return await call_next(request)
        try:
            # Extract database session
            db: AsyncSession = request.state.db

            # Extract current user
            current_user = await get_current_user(request)

            # Parse endpoint, HTTP method, and identify scope/context
            endpoint = request.url.path
            method = request.method
            scope, context_id = self.get_scope_and_context(endpoint)

            # Get user's role in the current context
            role = await self.get_user_role_in_context(current_user.id, scope, context_id, db)

            # Resolve effective permissions for the role
            effective_permissions = get_effective_permissions(role, scope)

            # Check if the user has access to the route and method
            if endpoint not in effective_permissions or method not in effective_permissions[endpoint]:
                raise HTTPException(status_code=403, detail="Permission denied")

            # Proceed with the request
            response = await call_next(request)
            return response

        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception as e:
            logger.error(f"Middleware error: {e}")
            return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    async def get_user_role_in_context(self, user_id: int, scope: str, context_id: int, db: AsyncSession) -> str:
        """
        Fetch the user's role in the specified context (organization or team).
        """
        if scope == "organization":
            org_user = await db.execute(
                select(OrganizationUser).where(
                    OrganizationUser.user_id == user_id, OrganizationUser.organization_id == context_id
                )
            )
            org_user = org_user.scalars().first()
            if not org_user:
                raise HTTPException(status_code=403, detail="User not part of the organization")
            return org_user.role.name

        elif scope == "team":
            team_member = await db.execute(
                select(TeamMember).where(
                    TeamMember.user_id == user_id, TeamMember.team_id == context_id
                )
            )
            team_member = team_member.scalars().first()
            if not team_member:
                raise HTTPException(status_code=403, detail="User not part of the team")
            return team_member.role.name

        raise HTTPException(status_code=400, detail="Invalid scope")

    def get_scope_and_context(self, endpoint: str) -> tuple:
        """
        Determine the scope (organization/team) and context ID (e.g., org_id, team_id) based on the endpoint.
        """
        if "/rbac/teams" in endpoint:
            return "team", self.extract_context_id_from_endpoint(endpoint, "teams")
        elif "/organizations" in endpoint:
            return "organization", self.extract_context_id_from_endpoint(endpoint, "organizations")
        raise HTTPException(status_code=403, detail="Invalid endpoint or insufficient scope")

    @staticmethod
    def extract_context_id_from_endpoint(endpoint: str, context_type: str) -> int:
        """
        Extract context ID (organization or team) from the endpoint.
        """
        import re
        match = re.search(f"/{context_type}/(\d+)", endpoint)
        if match:
            return int(match.group(1))
        raise HTTPException(status_code=400, detail=f"{context_type.capitalize()} ID not found in the endpoint")
    
    
async def initialize_roles():
    """
    Fetch roles from the database and store them in a global dictionary on server startup.
    """
    db = await anext(get_db())
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    settings.roles = [
        {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "scope": role.scope,
        }
        for role in roles
    ]
    await db.close()

def build_permissions():
    settings.permissions = {
    "organization": {
        "Admin": {
            "routes": {
                "/rbac/teams/create": ["POST"],
                "/rbac/teams/assign-user": ["POST"],
                "/rbac/teams/remove-user": ["DELETE"],
                "/rbac/teams": ["GET"]
            },
            "inherits": None,
        },
        "Member": {
            "routes": {
                "/rbac/teams": ["GET"]
            },
            "inherits": None,
        },
    },
    "team": {
        "Lead": {
            "routes": {
                "/rbac/teams/assign-user": ["POST"],
                "/rbac/teams/remove-user": ["DELETE"],
                "/rbac/teams": ["GET"]
            },
            "inherits": None,
        },
        "Team_Member": {
            "routes": {
                "/rbac/teams": ["GET"]
            },
            "inherits": None
        },
    },
    "super_admin": {
        "routes": {
            "*": ["GET", "POST", "PUT", "DELETE", "PATCH"]
        },
        "inherits": None
    }
}
