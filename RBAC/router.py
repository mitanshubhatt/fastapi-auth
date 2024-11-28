from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.connection import get_db
from auth.models import User
from RBAC.models import (
    Organization,
    OrganizationUser,
    Team,
    TeamMember,
    Role
)
from RBAC.schemas import (
    OrganizationCreate,
    OrganizationRead,
    TeamCreate,
    TeamRead
)
from auth.dependencies import get_current_user
from utils.custom_logger import logger

router = APIRouter(prefix="/rbac")


@router.post("/create-organization", response_model=OrganizationRead, tags=["Organizations"])
async def create_organization(
    org: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Create the organization
        db_org = Organization(name=org.name)
        db.add(db_org)
        await db.commit()
        await db.refresh(db_org)

        # Assign the current user as admin of the organization
        admin_role = await db.execute(select(Role).where(Role.name == "Admin"))
        admin_role = admin_role.scalars().first()
        if not admin_role:
            raise HTTPException(status_code=500, detail="Admin role not found")

        org_user = OrganizationUser(
            organization_id=db_org.id,
            user_id=current_user.id,
            role_id=admin_role.id
        )
        db.add(org_user)
        await db.commit()
        await db.refresh(org_user)

        return OrganizationRead.from_orm(db_org)
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/assign-user-to-organization", tags=["Organizations"])
async def assign_user_to_organization(
    user_email: str,
    organization_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Ensure current user is an organization admin
        org_user = await db.execute(
            select(OrganizationUser)
            .where(OrganizationUser.user_id == current_user.id, OrganizationUser.organization_id == organization_id)
        )
        org_user = org_user.scalars().first()
        if not org_user or org_user.role.name != "Admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Fetch the user by email
        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Assign the user to the organization
        org_user = OrganizationUser(
            organization_id=organization_id,
            user_id=user.id,
            role_id=role_id
        )
        db.add(org_user)
        await db.commit()
        return {"message": "User assigned to organization successfully"}
    except Exception as e:
        logger.error(f"Error assigning user to organization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/create-team", response_model=TeamRead, tags=["Teams"])
async def create_team(
    team: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Check if the user is an admin of the organization
        org_user = await db.execute(
            select(OrganizationUser)
            .where(OrganizationUser.user_id == current_user.id, OrganizationUser.organization_id == team.organization_id)
        )
        org_user = org_user.scalars().first()
        if not org_user or org_user.role.name != "Admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Create the team
        db_team = Team(organization_id=team.organization_id, name=team.name)
        db.add(db_team)
        await db.commit()
        await db.refresh(db_team)
        return TeamRead.from_orm(db_team)
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/assign-user-to-team", tags=["Teams"])
async def assign_user_to_team(
    user_email: str,
    team_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Ensure current user is a team admin
        team_member = await db.execute(
            select(TeamMember)
            .where(TeamMember.user_id == current_user.id, TeamMember.team_id == team_id)
        )
        team_member = team_member.scalars().first()
        if not team_member or team_member.role.name != "Team Admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Fetch the user by email
        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Assign the user to the team
        team_member = TeamMember(team_id=team_id, user_id=user.id, role_id=role_id)
        db.add(team_member)
        await db.commit()
        return {"message": "User assigned to team successfully"}
    except Exception as e:
        logger.error(f"Error assigning user to team: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/roles", tags=["Roles"])
async def get_roles(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all roles available in the system.
    """
    try:
        result = await db.execute(select(Role))
        roles = result.scalars().all()
        return [{"id": role.id, "name": role.name, "description": role.description} for role in roles]
    except Exception as e:
        logger.error(f"Error retrieving roles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/current-role/organization/{organization_id}", tags=["Roles"])
async def get_current_user_role_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the current user's role in a specific organization.
    """
    try:
        org_user = await db.execute(
            select(OrganizationUser).where(
                OrganizationUser.user_id == current_user.id,
                OrganizationUser.organization_id == organization_id
            )
        )
        org_user = org_user.scalars().first()
        if not org_user:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"organization_id": organization_id, "role_id": org_user.role.id, "role_name": org_user.role.name}
    except Exception as e:
        logger.error(f"Error retrieving user's role in organization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/current-role/team/{team_id}", tags=["Roles"])
async def get_current_user_role_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the current user's role in a specific team.
    """
    try:
        team_member = await db.execute(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id,
                TeamMember.team_id == team_id
            )
        )
        team_member = team_member.scalars().first()
        if not team_member:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"team_id": team_id, "role_id": team_member.role.id, "role_name": team_member.role.name}
    except Exception as e:
        logger.error(f"Error retrieving user's role in team: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
