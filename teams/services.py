# RBAC/services/team_service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from roles.dao import RoleDAO
from teams.dao import TeamDAO
from organizations.dao import OrganizationDAO
from auth.dao import UserDAO
from utils.encryption import DataEncryptor
from teams.schemas import TeamCreate, TeamRead
from auth.models import User as AuthUser
from utils.custom_logger import logger


class TeamService:
    def __init__(self, db: AsyncSession):
        self.team_dao = TeamDAO(db=db)
        self.organization_dao = OrganizationDAO(db=db)
        self.encryptor = DataEncryptor(settings.encryption_key)
        self.roles_dao = RoleDAO(db=db)
        self.user_dao = UserDAO(encryptor=self.encryptor, db=db)

    async def create_team(
            self, db: AsyncSession, team_create_data: TeamCreate, current_user: AuthUser
    ) -> TeamRead:
        """
        Creates a new team if the current user is an admin of the organization.
        """
        org_membership = await self.organization_dao.get_organization_user(
            user_id=current_user.id, organization_id=team_create_data.organization_id
        )
        if not org_membership or not org_membership.role or org_membership.role.name != "Admin":
            logger.warn(
                f"User {current_user.id} (email: {await self.encryptor.decrypt(current_user.email) if current_user.email else 'N/A'}) "
                f"attempted to create team in org {team_create_data.organization_id} without Admin role."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to create a team in this organization."
            )

        # 2. Create Team
        try:
            db_team = await self.team_dao.create_team(team_create_data)
            return TeamRead.model_validate(db_team)
        except Exception as e:
            logger.error(f"Error during team creation in service: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the team."
            )

    async def assign_user_to_team(
            self, plain_user_email: str, team_id: int, role_id: int, current_user: AuthUser
    ):
        """
        Assigns a user to a team if the current user is a team admin/lead.
        """
        actor_team_membership = await self.team_dao.get_team_member_role(user_id=current_user.id, team_id=team_id)

        assigner_roles = ["Team Lead", "Admin"]

        if not actor_team_membership or not actor_team_membership.role or actor_team_membership.role.name not in assigner_roles:
            # Fallback: Check if current_user is an Org Admin for the team's organization
            team = await self.team_dao.get_team_by_id(team_id)
            if not team:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")

            org_membership = await self.organization_dao.get_organization_user(
                user_id=current_user.id, organization_id=team.organization_id
            )
            if not org_membership or not org_membership.role or org_membership.role.name != "Admin":
                logger.warn(
                    f"User {current_user.id} (email: {await self.encryptor.decrypt(current_user.email) if current_user.email else 'N/A'}) "
                    f"attempted to assign user to team {team_id} without required role (Team Lead/Admin or Org Admin)."
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to assign users to this team."
                )

        # 2. Fetch the target user by plaintext email
        target_user = await self.user_dao.get_user_by_email(plain_user_email)
        if not target_user:
            logger.info(f"Attempted to assign non-existent user (email: {plain_user_email}) to team {team_id}.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to be assigned not found.")

        # 3. Fetch the role to be assigned
        target_role = await self.roles_dao.get_role_by_id(role_id)
        if not target_role:
            logger.warn(f"Attempted to assign non-existent role ID {role_id} in team {team_id}.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role to be assigned not found.")
        if target_role.scope != "team":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid role scope for team assignment.")

        existing_membership = await self.team_dao.get_team_member(user_id=target_user.id, team_id=team_id)
        if existing_membership:
            logger.info(f"User {plain_user_email} is already a member of team {team_id}.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,  # 409 Conflict
                detail="User is already a member of this team."
            )

        # 5. Assign user to team
        try:
            encrypted_target_email = target_user.email
            user_full_name = f"{target_user.first_name} {target_user.last_name}".strip()

            await self.team_dao.add_user_to_team(
                team_id, target_user.id, role_id,
                user_email_encrypted=encrypted_target_email,
                user_name=user_full_name,
                role_name=target_role.name
            )
            return {"message": "User assigned to team successfully."}
        except Exception as e:
            logger.error(f"Error assigning user {plain_user_email} to team {team_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while assigning the user to the team."
            )

    async def remove_user_from_team(
            self, db: AsyncSession, plain_user_email: str, team_id: int, current_user: AuthUser
    ):
        """
        Removes a user from a team.
        Requires current_user to be a Team Lead/Admin of the team or an Org Admin of the team's organization.
        """
        # 1. Permission Check (similar to assign_user_to_team)
        actor_team_membership = await self.team_dao.get_team_member_role(user_id=current_user.id, team_id=team_id)

        remover_roles = ["Team Lead", "Admin"]  # Customize as needed

        can_remove = False
        if actor_team_membership and actor_team_membership.role and actor_team_membership.role.name in remover_roles:
            can_remove = True

        if not can_remove:
            team = await self.team_dao.get_team_by_id(team_id)
            if not team:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")

            org_membership = await self.organization_dao.get_organization_user(
                user_id=current_user.id, organization_id=team.organization_id
            )
            if org_membership and org_membership.role and org_membership.role.name == "Admin":
                can_remove = True

        if not can_remove:
            logger.warn(
                f"User {current_user.id} (email: {await self.encryptor.decrypt(current_user.email) if current_user.email else 'N/A'}) "
                f"attempted to remove user from team {team_id} without required role."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to remove users from this team."
            )

        # 2. Fetch the target user by plaintext email
        target_user = await self.user_dao.get_user_by_email(plain_user_email)
        if not target_user:
            logger.info(f"Attempted to remove non-existent user (email: {plain_user_email}) from team {team_id}.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to be removed not found.")

        # 3. Find the team membership
        team_membership_to_remove = await self.team_dao.get_team_member(user_id=target_user.id, team_id=team_id)
        if not team_membership_to_remove:
            logger.info(f"User {plain_user_email} is not a member of team {team_id}.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this team."
            )

        # Prevent user from removing themselves if they are the sole Team Lead (optional business rule)
        # This logic can be more complex depending on requirements.
        if target_user.id == current_user.id and actor_team_membership and actor_team_membership.role.name == "Team Lead":
            # Add logic here to check if they are the *only* Team Lead.
            pass

        # 4. Remove user from team
        try:
            await self.team_dao.remove_team_member(team_membership_to_remove)
            return {"message": f"User {plain_user_email} successfully removed from team {team_id}."}
        except Exception as e:
            logger.error(f"Error removing user {plain_user_email} from team {team_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while removing the user from the team."
            )
