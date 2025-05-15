from sqlalchemy import Integer, Column, String, Index, ForeignKey, Enum, Text

from db.pg_connection import Base



class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)

    member_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_team_org_name', 'organization_id', 'name', unique=True),
    )


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)

    role_name = Column(String)  # Denormalized role name
    user_email = Column(String)  # Denormalized user email for faster display
    user_name = Column(String)  # Denormalized user name

    __table_args__ = (
        Index('idx_team_user', 'team_id', 'user_id', unique=True),
        Index('idx_user_teams', 'user_id', 'team_id'),
    )
