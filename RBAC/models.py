from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db.connection import Base
from datetime import datetime
import enum


class RoleType(enum.Enum):
    ADMIN = "Admin"
    MEMBER = "Member"

class TeamRoleType(enum.Enum):
    TEAM_ADMIN = "TeamAdmin"
    MEMBER = "Member"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)

    organization_users = relationship("OrganizationUser", back_populates="organization")
    teams = relationship("Team", back_populates="organization")

class OrganizationUser(Base):
    __tablename__ = "organization_users"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # Assuming User model is defined elsewhere with 'id' as PK
    role = Column(Enum(RoleType), nullable=False)

    organization = relationship("Organization", back_populates="organization_users")
    user = relationship("User", back_populates="organization_users", foreign_keys=[user_id])

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    name = Column(String, nullable=False)

    organization = relationship("Organization", back_populates="teams")
    team_members = relationship("TeamMember", back_populates="team")

class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # Assuming User model is defined elsewhere with 'id' as PK
    role = Column(Enum(TeamRoleType), nullable=False)

    team = relationship("Team", back_populates="team_members")
    user = relationship("User", back_populates="team_members", foreign_keys=[user_id])
