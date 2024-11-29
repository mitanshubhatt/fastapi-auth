from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from db.connection import Base
from datetime import datetime


class RolePermission(Base):
    __tablename__ = 'role_permission'

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    permission_id = Column(Integer, ForeignKey('permissions.id'))

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

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
    role_id = Column(Integer, ForeignKey("roles.id"))

    organization = relationship("Organization", back_populates="organization_users")
    user = relationship("User", back_populates="organization_users", foreign_keys=[user_id])
    role = relationship("Role", back_populates="organization_users")

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
    role_id = Column(Integer, ForeignKey("roles.id"))

    team = relationship("Team", back_populates="team_members")
    user = relationship("User", back_populates="team_members", foreign_keys=[user_id])
    role = relationship("Role", back_populates="team_members")

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    scope = Column(Enum("organization", "team", name="role_scope"), nullable=False)

    role_permissions = relationship("RolePermission", back_populates="role")
    organization_users = relationship("OrganizationUser", back_populates="role")
    team_members = relationship("TeamMember", back_populates="role")


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Permission name (e.g., create_team, assign_task)
    description = Column(String)
    scope = Column(Enum("organization", "team", name="permission_scope"), nullable=False)  # Permission scope

    role_permissions = relationship("RolePermission", back_populates="permission")


class UserRole(Base):
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
