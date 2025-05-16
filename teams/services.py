from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from organizations.dao import OrganizationDAO
from teams.dao import TeamDAO
from auth.dao import UserDAO
from teams.models import Team
from teams.schemas import TeamCreate
from auth.models import User
from utils.custom_logger import logger

class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_user_dao = OrganizationDAO(db)
        self.team_dao = TeamDAO(db)
        self.team_member_dao = TeamDAO(db)
        self.user_dao = UserDAO(db)

    async def create_team(self, team_data: TeamCreate, current_user: User) -> Team:
        """
        Creates a team if the current user is an admin of the organization.
        """
        org_user = await self.org_user_dao.get_organization_user(
            user_id=current_user.id,
            organization_id=team_data.organization_id
        )

        if not org_user or not org_user.role or org_user.role.name != "Admin":
            logger.warning(
                f"User {current_user.id} lacks Admin permissions in organization {team_data.organization_id} to create team."
            )
            raise HTTPException(status_code=403, detail="Not enough permissions to create team.")

        try:
            db_team = await self.team_dao.create_team(
                organization_id=team_data.organization_id,
                name=team_data.name
            )
            logger.info(f"Team '{db_team.name}' (ID: {db_team.id}) created successfully by user {current_user.id}.")
            return db_team
        except Exception as e:
            logger.error(f"Database error creating team: {e}")
            raise HTTPException(status_code=500, detail="Failed to create team due to a database error.")


    async def assign_user_to_team(self, user_email: str, team_id: int, role_id: int, current_user: User) -> None:
        """
        Assigns a user to a team if the current user is a team admin.
        """
        current_team_member = await self.team_member_dao.get_team_member(
            user_id=current_user.id,
            team_id=team_id
        )
        if not current_team_member or not current_team_member.role or current_team_member.role.name != "Team Admin":
            logger.warning(
                f"User {current_user.id} lacks Team Admin permissions for team {team_id} to assign user."
            )
            raise HTTPException(status_code=403, detail="Not enough permissions to assign user to this team.")

        team = await self.team_dao.get_team_by_id(team_id)
        if not team:
            logger.warning(f"Attempt to assign user to non-existent team ID: {team_id} by user {current_user.id}")
            raise HTTPException(status_code=404, detail="Team not found.")

        # 3. Fetch the user to be assigned by email
        user_to_assign = await self.user_dao.get_user_by_email(user_email)
        if not user_to_assign:
            logger.warning(f"User with email '{user_email}' not found for team assignment by user {current_user.id}.")
            raise HTTPException(status_code=404, detail=f"User with email '{user_email}' not found.")

        # 4. Check if the user is already in the team (optional, but good practice)
        existing_assignment = await self.team_member_dao.get_team_member(
            user_id=user_to_assign.id,
            team_id=team_id
        )
        if existing_assignment:
            logger.info(f"User {user_to_assign.id} is already a member of team {team_id}.")
            # Depending on requirements, you might raise an error or just return successfully
            raise HTTPException(status_code=409, detail="User is already a member of this team.")
            # return # Or simply do nothing if idempotent assignment is desired

        # 5. Assign the user to the team
        try:
            await self.team_member_dao.add_user_to_team(
                user_id=user_to_assign.id,
                team_id=team_id,
                role_id=role_id
            )
            logger.info(
                f"User '{user_email}' (ID: {user_to_assign.id}) assigned to team {team_id} with role {role_id} by user {current_user.id}."
            )
        except Exception as e:
            logger.error(f"Database error assigning user to team: {e}")
            raise HTTPException(status_code=500, detail="Failed to assign user to team due to a database error.")


    async def remove_user_from_team(self, user_email: str, team_id: int, current_user: User) -> None:
        """
        Removes a user from a team.
        For simplicity, this example assumes any authenticated user can attempt this,
        but in a real scenario, you'd add permission checks (e.g., org admin, team admin, or the user themselves).
        Let's assume for this refactor that the original logic (no specific permission check for remover) is maintained.
        If specific permissions are needed for the *remover*, they should be added here.
        """
        # 1. Fetch the team to ensure it exists
        team = await self.team_dao.get_team_by_id(team_id)
        if not team:
            logger.warning(f"Attempt to remove user from non-existent team ID: {team_id} by user {current_user.id}")
            raise HTTPException(status_code=404, detail="Team not found.")

        # 2. Fetch the user to be removed by email
        user_to_remove = await self.user_dao.get_user_by_email(user_email)
        if not user_to_remove:
            logger.warning(f"User with email '{user_email}' not found for team removal by user {current_user.id}.")
            raise HTTPException(status_code=404, detail=f"User with email '{user_email}' not found.")

        team_member_to_remove = await self.team_member_dao.get_team_member(
            user_id=user_to_remove.id,
            team_id=team_id
        )
        if not team_member_to_remove:
            logger.warning(
                f"User '{user_email}' (ID: {user_to_remove.id}) is not part of team {team_id}. Removal requested by {current_user.id}."
            )
            raise HTTPException(status_code=404, detail="User is not part of this team.")

        try:
            await self.team_member_dao.remove_user_from_team(team_member_to_remove)
            logger.info(
                f"User '{user_email}' (ID: {user_to_remove.id}) removed from team {team_id} by user {current_user.id}."
            )
        except Exception as e:
            logger.error(f"Database error removing user from team: {e}")
            raise HTTPException(status_code=500, detail="Failed to remove user from team due to a database error.")