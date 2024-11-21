from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from db.connection import get_db
from auth.models import User
from RBAC.models import Organization, OrganizationUser, Team, TeamMember, RoleType, TeamRoleType
from RBAC.schemas import OrganizationCreate, OrganizationRead, TeamCreate, TeamRead, OrganizationUserRead, TeamMemberRead
from auth.dependencies import get_current_user
from utils.custom_logger import logger

router = APIRouter(prefix="/rbac")

@router.post("/create-organization", response_model=OrganizationRead, description="Create a new organization. Only admin users can perform this action.", tags=["Organizations"])
async def create_organization(org: OrganizationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        db_org = Organization(name=org.name)
        db.add(db_org)
        
        # Add the current user as the admin of the organization
        org_user = OrganizationUser(
            organization_id=db_org.id,
            user_id=current_user.id,
            role=RoleType.ADMIN
        )
        db.add(org_user)
        await db.commit()
        await db.refresh(org_user)
        await db.refresh(db_org)

        # logger.info(f"Organization '{org.name}' created successfully with {current_user.email} as admin.")
        return OrganizationRead.from_orm(db_org)
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/assign-user-to-organization", description="Assign a user to an organization with a specified role. Only admin users can perform this action.", tags=["Organizations"])
async def assign_user_to_organization(user_email: str, organization_id: int, role: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Assigns a user to an organization with a specified role using the user's email.

    Parameters:
    - user_email (str): The email of the user to be assigned.
    - organization_id (int): The ID of the organization to which the user will be assigned.
    - role (str): The role to be assigned to the user within the organization.
    - db (AsyncSession, optional): The database session dependency, defaulting to the result of get_db.
    - current_user (User, optional): The current user dependency, defaulting to the result of get_current_user.

    Returns:
    - dict: A dictionary containing a success message if the operation is successful.

    Raises:
    - HTTPException: If the current user is not an admin, a 403 Forbidden error is raised.
    - HTTPException: If the user or organization is not found, a 404 Not Found error is raised.
    - HTTPException: If any other error occurs during the operation, a 500 Internal Server Error is raised.
    """
    if not current_user.is_admin:
        logger.error("Permission denied: User is not an admin.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    try:
        # Fetch the user by email
        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        organization = await db.get(Organization, organization_id)
        enum_role = RoleType(role)
        if not user or not organization:
            logger.error("User or Organization not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or Organization not found")
        org_user = OrganizationUser(user_id=user.id, organization_id=organization_id, role=enum_role)
        db.add(org_user)
        await db.commit()
        logger.info(f"User {user_email} assigned to organization {organization_id} with role {role}.")
        return {"message": "User assigned to organization successfully"}
    except Exception as e:
        logger.error(f"Error assigning user to organization: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")



@router.post("/create-team", response_model=TeamRead, description="Create a new team within an organization. Only organization admins can perform this action.", tags=["Teams"])
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_role = await db.execute(
        select(OrganizationUser.role).where(
            OrganizationUser.user_id == current_user.id,
            OrganizationUser.organization_id == team.organization_id
        )
    )
    user_role = user_role.scalar()

    if user_role == RoleType.ADMIN:
        try:
            db_team = Team(organization_id=team.organization_id, product_id=team.product_id, name=team.name)
            db.add(db_team)
            await db.commit()
            await db.refresh(db_team)
            logger.info(f"Team '{team.name}' created successfully.")
            return TeamRead.from_orm(db_team)
        except Exception as e:
            logger.error(f"Error creating team: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    else:
        logger.error("Permission denied: User is not an organization admin.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


@router.post("/assign-user-to-team", description="Assign a user to a team. Only team admins can perform this action.", tags=["Teams"])
async def assign_user_to_team(user_email: str, team_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Assigns a user to a specified team in the database.

    Parameters:
    - user_email (str): The email of the user to be assigned to the team.
    - team_id (int): The ID of the team to which the user will be assigned.
    - db (AsyncSession): The database session used for executing queries. Defaults to a dependency injection of `get_db`.
    - current_user (User): The current user making the request. Defaults to a dependency injection of `get_current_user`.

    Returns:
    - dict: A dictionary containing a success message if the user is successfully assigned to the team.

    Raises:
    - HTTPException: 
        - 403 Forbidden: If the current user is not an admin.
        - 404 Not Found: If the user or team is not found in the database.
        - 500 Internal Server Error: If an unexpected error occurs during the operation.
    """
    user_role = await db.execute(
        select(TeamMember.role).where(
            TeamMember.user_id == current_user.id,
            TeamMember.team_id == team_id
        )
    )
    user_role = user_role.scalar()

    if user_role == TeamRoleType.TEAM_ADMIN:
        # Fetch the user by email
        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        team_member = TeamMember(team_id=team_id, user_id=user.id, role=TeamRoleType.MEMBER)
        db.add(team_member)
        await db.commit()
        return {"message": "User added to team successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")



@router.get("/organization-users/{organization_id}", response_model=List[OrganizationUserRead], description="Retrieve a list of users associated with a specific organization. Only admins can access this information.", tags=["Organizations"])
async def get_organization_users(organization_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a list of users associated with a specific organization.

    Parameters:
    - organization_id (int): The unique identifier of the organization whose users are to be retrieved.
    - db (AsyncSession): The database session used to execute the query. It is injected via dependency.
    - current_user (User): The current authenticated user making the request. It is injected via dependency.

    Returns:
    - List[OrganizationUserRead]: A list of users associated with the specified organization, represented as `OrganizationUserRead` objects.

    Raises:
    - HTTPException: If the current user is not an admin, a 403 Forbidden error is raised.
    - HTTPException: If there is an error during the database query execution, a 500 Internal Server Error is raised.
    """
    if not current_user.is_admin:
        logger.error("Permission denied: User is not an admin.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    try:
        result = await db.execute(select(OrganizationUser).where(OrganizationUser.organization_id == organization_id))
        organization_users = result.scalars().all()
        logger.info(f"Retrieved users for organization {organization_id}.")
        return [OrganizationUserRead.from_orm(org_user) for org_user in organization_users]
    except Exception as e:
        logger.error(f"Error retrieving organization users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/team-members/{team_id}", response_model=List[TeamMemberRead], description="Retrieve the list of team members for a specified team. Only admins can access this information.", tags=["Teams"])
async def get_team_members(team_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve the list of team members for a specified team.

    Parameters:
    - team_id (int): The unique identifier of the team whose members are to be retrieved.
    - db (AsyncSession): The database session used to execute the query. It is injected by dependency.
    - current_user (User): The current authenticated user making the request. It is injected by dependency.

    Returns:
    - List[TeamMemberRead]: A list of team members represented as `TeamMemberRead` objects.

    Raises:
    - HTTPException: 
        - 403 Forbidden: If the current user is not an admin and lacks the necessary permissions.
        - 500 Internal Server Error: If there is an error during the retrieval of team members.
    """
    if not current_user.is_admin:
        logger.error("Permission denied: User is not an admin.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    try:
        result = await db.execute(select(TeamMember).where(TeamMember.team_id == team_id))
        team_members = result.scalars().all()
        logger.info(f"Retrieved members for team {team_id}.")
        return [TeamMemberRead.from_orm(team_member) for team_member in team_members]
    except Exception as e:
        logger.error(f"Error retrieving team members: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/change-user-role", description="Change the role of a user in an organization. Only organization admins can perform this action.", tags=["Organizations"])
async def change_user_role(user_id: int, organization_id: int, new_role: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Change the role of a user in an organization.

    Parameters:
    - user_id (int): The ID of the user whose role is to be changed.
    - organization_id (int): The ID of the organization.
    - new_role (str): The new role to assign to the user.

    Returns:
    - dict: A message indicating the success of the operation.

    Raises:
    - HTTPException: If the current user is not authorized to change roles or if the user/organization is not found.
    """
    user_role = await db.execute(
        select(OrganizationUser.role).where(
            OrganizationUser.user_id == current_user.id,
            OrganizationUser.organization_id == organization_id
        )
    )
    user_role = user_role.scalar()

    if user_role != RoleType.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    try:
        result = await db.execute(
            update(OrganizationUser)
            .where(OrganizationUser.user_id == user_id, OrganizationUser.organization_id == organization_id)
            .values(role=RoleType(new_role))
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or Organization not found")
        await db.commit()
        return {"message": "User role updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/change-team-role", description="Change the role of a user in a team. Only team admins can perform this action.", tags=["Teams"])
async def change_team_role(user_id: int, team_id: int, new_role: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Change the role of a user in a team.

    Parameters:
    - user_id (int): The ID of the user whose role is to be changed.
    - team_id (int): The ID of the team.
    - new_role (str): The new role to assign to the user.

    Returns:
    - dict: A message indicating the success of the operation.

    Raises:
    - HTTPException: If the current user is not authorized to change roles or if the user/team is not found.
    """
    # Check if the current user is a team admin
    user_role = await db.execute(
        select(TeamMember.role).where(
            TeamMember.user_id == current_user.id,
            TeamMember.team_id == team_id
        )
    )
    user_role = user_role.scalar()

    if user_role != TeamRoleType.TEAM_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    try:
        result = await db.execute(
            update(TeamMember)
            .where(TeamMember.user_id == user_id, TeamMember.team_id == team_id)
            .values(role=TeamRoleType(new_role))
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or Team not found")
        await db.commit()
        return {"message": "User role updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/organizations", description="Retrieve a list of all organizations along with the roles of the current user.", tags=["Organizations"])
async def list_organizations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a list of all organizations along with the roles of the current user.

    Parameters:
    - db (AsyncSession): The database session used to execute the query. It is injected via dependency.
    - current_user (User): The current authenticated user making the request. It is injected via dependency.

    Returns:
    - List[OrganizationRead]: A list of all organizations with the user's roles.

    Raises:
    - HTTPException: If there is an error during the database query execution, a 500 Internal Server Error is raised.
    """
    try:
        result = await db.execute(
            select(Organization, OrganizationUser.role)
            .join(OrganizationUser, Organization.id == OrganizationUser.organization_id)
            .where(OrganizationUser.user_id == current_user.id)
        )
        organizations_with_roles = result.all()
        return [
            {
                "organization": OrganizationRead.from_orm(org),
                "role": role
            }
            for org, role in organizations_with_roles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/teams", description="Retrieve a list of all teams along with the roles of the current user.", tags=["Teams"])
async def list_teams(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieve a list of all teams along with the roles of the current user.

    Parameters:
    - db (AsyncSession): The database session used to execute the query. It is injected via dependency.
    - current_user (User): The current authenticated user making the request. It is injected via dependency.

    Returns:
    - List[TeamRead]: A list of all teams with the user's roles.

    Raises:
    - HTTPException: If there is an error during the database query execution, a 500 Internal Server Error is raised.
    """
    try:
        result = await db.execute(
            select(Team, TeamMember.role)
            .join(TeamMember, Team.id == TeamMember.team_id)
            .where(TeamMember.user_id == current_user.id)
        )
        teams_with_roles = result.all()
        return [
            {
                "team": TeamRead.from_orm(team),
                "role": role
            }
            for team, role in teams_with_roles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")