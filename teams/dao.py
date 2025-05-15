# RBAC/dao/team_dao.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from roles.models import Role

from teams.models import Team, TeamMember
from organizations.models import Organization

from teams.schemas import TeamCreate
from utils.custom_logger import logger


class TeamDAO:

    def __init__(self, db: AsyncSession):
        """
        Initializes the TeamDAO with an asynchronous database session.

        Args:
            db: The AsyncSession for database operations.
        """
        self.db: AsyncSession = db

    async def create_team(self, team_data: TeamCreate) -> Team:
        """
        Creates a new team in the database and increments the team_count on the organization.

        Args:
            team_data: The Pydantic schema containing team creation data.

        Returns:
            The created Team object.
        """
        db_team = Team(organization_id=team_data.organization_id, name=team_data.name, member_count=0)
        self.db.add(db_team)

        # Increment team_count in the Organization model
        # Using await self.db.get() which is suitable for fetching by primary key.
        organization = await self.db.get(Organization, team_data.organization_id)
        if organization:
            organization.team_count = (organization.team_count or 0) + 1
            self.db.add(organization) # Add to session if changes were made
        else:
            logger.warn(f"Organization with ID {team_data.organization_id} not found for team count update.")

        await self.db.commit()
        await self.db.refresh(db_team)
        if organization: # Refresh organization if it was modified and you need updated state
             await self.db.refresh(organization)
        logger.info(f"Team '{db_team.name}' created successfully for organization ID {db_team.organization_id}.")
        return db_team

    async def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """
        Fetches a team by its ID, eagerly loading its organization.

        Args:
            team_id: The ID of the team to fetch.

        Returns:
            The Team object if found, otherwise None.
        """
        result = await self.db.execute(
            select(Team).where(Team.id == team_id)
        )
        return result.scalars().first()

    async def get_team_member_with_role(self, user_id: int, team_id: int) -> Optional[TeamMember]:
        """
        Fetches a team member's record, including their role, for a specific team.
        (Renamed from get_team_member_role for clarity, as it returns the TeamMember object)

        Args:
            user_id: The ID of the user.
            team_id: The ID of the team.

        Returns:
            The TeamMember object with its role eagerly loaded, if found, otherwise None.
        """
        stmt = (
            select(
                TeamMember,
                Role.description.label("role_description_from_table"),
                Role.scope.label("role_scope_from_table")
            )
            .join(Role, TeamMember.role_id == Role.id)
            .where(TeamMember.user_id == user_id, TeamMember.team_id == team_id)
        )

        result_row = await self.db.execute(stmt)
        record = result_row.first()  # Fetches a single RowProxy object or None

        if record:
            team_member_obj = record.TeamMember

            team_member_obj.role_description = record.role_description_from_table
            team_member_obj.role_scope = record.role_scope_from_table

            return team_member_obj
        return None


    async def add_user_to_team(
            self, team_id: int, user_id: int, role_id: int,
            user_email_encrypted: str, user_name: str, role_name: str
    ) -> TeamMember:
        """
        Adds a user to a team with a specific role and increments the team's member_count.

        Args:
            team_id: The ID of the team.
            user_id: The ID of the user to add.
            role_id: The ID of the role to assign.
            user_email_encrypted: (Denormalized) User's encrypted email.
            user_name: (Denormalized) User's name.
            role_name: (Denormalized) Role's name.

        Returns:
            The created TeamMember object.
        """
        existing_member = await self.get_team_member_with_role(user_id, team_id)
        if existing_member:
            logger.info(f"User ID {user_id} is already a member of team ID {team_id}.")
            return existing_member

        new_team_member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role_id=role_id,
            user_email=user_email_encrypted,
            user_name=user_name,
            role_name=role_name
        )
        self.db.add(new_team_member)

        # Increment member_count in the Team model
        team = await self.db.get(Team, team_id)
        if team:
            team.member_count = (team.member_count or 0) + 1
            self.db.add(team) # Add to session if changes were made
        else:
            logger.warn(f"Team with ID {team_id} not found for member count update.")

        await self.db.commit()
        await self.db.refresh(new_team_member)
        if team: # Refresh team if it was modified
            await self.db.refresh(team)
        logger.info(f"User ID {user_id} added to team ID {team_id} with role ID {role_id}.")
        return new_team_member

    async def get_team_member(self, user_id: int, team_id: int) -> Optional[TeamMember]:
        """
        Fetches a specific team member record.

        Args:
            user_id: The ID of the user.
            team_id: The ID of the team.

        Returns:
            The TeamMember object if found, otherwise None.
        """
        result = await self.db.execute(
            select(TeamMember).where(TeamMember.user_id == user_id, TeamMember.team_id == team_id)
        )
        return result.scalars().first()


    async def get_team_member_role(self, user_id: int, team_id: int) -> Optional[TeamMember]:
        """
        Fetches a specific team member record.

        Args:
            user_id: The ID of the user.
            team_id: The ID of the team.

        Returns:
            The TeamMember object if found, otherwise None.
        """
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.user_id == user_id,
                TeamMember.team_id == team_id
            )
        )
        return result.scalars().first()

    async def remove_team_member(self, team_member: TeamMember) -> None:
        """
        Removes a team member from a team and decrements the team's member_count.

        Args:
            team_member: The TeamMember object to delete.
        """
        team_id = team_member.team_id
        await self.db.delete(team_member)

        # Decrement member_count in the Team model
        team = await self.db.get(Team, team_id)
        if team:
            team.member_count = max(0, (team.member_count or 0) - 1)
            self.db.add(team)
        else:
            logger.warn(f"Team with ID {team_id} not found for member count update during removal.")

        await self.db.commit()
        if team:
            await self.db.refresh(team)
        logger.info(f"Team member ID {team_member.id} (User ID: {team_member.user_id}, Team ID: {team_id}) removed.")

