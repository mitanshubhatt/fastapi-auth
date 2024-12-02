from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from RBAC.models import Team, TeamMember, OrganizationUser
from RBAC.schemas import TeamCreate, TeamRead
from auth.models import User
from utils.custom_logger import logger


async def create_team_view(team: TeamCreate, db: AsyncSession, current_user: User):
    try:
        # Check if the user is an admin of the organization
        org_user = await db.execute(
            select(OrganizationUser).where(
                OrganizationUser.user_id == current_user.id,
                OrganizationUser.organization_id == team.organization_id,
            )
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


async def assign_user_to_team_view(user_email: str, team_id: int, role_id: int, db: AsyncSession, current_user: User):
    try:
        # Ensure current user is a team admin
        team_member = await db.execute(
            select(TeamMember).where(
                TeamMember.user_id == current_user.id,
                TeamMember.team_id == team_id,
            )
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
        new_team_member = TeamMember(team_id=team_id, user_id=user.id, role_id=role_id)
        db.add(new_team_member)
        await db.commit()
        return {"message": "User assigned to team successfully"}
    except Exception as e:
        logger.error(f"Error assigning user to team: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def remove_user_from_team_view(
    user_email: str, team_id: int, db: AsyncSession, current_user: User
):
    try:
        user = await db.execute(select(User).where(User.email == user_email))
        user = user.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        team_member = await db.execute(
            select(TeamMember)
            .where(TeamMember.user_id == user.id, TeamMember.team_id == team_id)
        )
        team_member = team_member.scalars().first()
        if not team_member:
            raise HTTPException(status_code=404, detail="User is not part of the team")

        # Remove the user from the team
        await db.delete(team_member)
        await db.commit()

        return {"message": f"User {user_email} successfully removed from team {team_id}"}

    except Exception as e:
        logger.error(f"Error removing user from team: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")