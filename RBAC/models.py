import time

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Index, Text
from db.pg_connection import Base


class RolePermission(Base):
    __tablename__ = 'role_permission'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False, index=True)

    permission_name = Column(String)

    __table_args__ = (
        Index('idx_role_permission_unique', 'role_id', 'permission_id', unique=True),
    )


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    creation_epoch = Column(Integer, default=int(time.time()))

    user_count = Column(Integer, default=0)
    team_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_org_name_date', 'name', 'creation_epoch'),
    )


class OrganizationUser(Base):
    __tablename__ = "organization_users"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)

    # Denormalize key information from related tables
    role_name = Column(String)  # Denormalized role name for quick access
    user_name = Column(String)  # Denormalized user name for quick listing

    __table_args__ = (
        # Composite indexes for common access patterns
        Index('idx_org_user', 'organization_id', 'user_id', unique=True),
        Index('idx_user_role', 'user_id', 'role_id'),
    )


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)

    # Denormalized fields
    member_count = Column(Integer, default=0)  # Counter cache for members

    __table_args__ = (
        # Composite index for organization teams lookups
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
        # Composite indexes for common access patterns
        Index('idx_team_user', 'team_id', 'user_id', unique=True),
        Index('idx_user_teams', 'user_id', 'team_id'),
    )


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    scope = Column(Enum("organization", "team", name="role_scope"), nullable=False, index=True)

    permissions_cache = Column(Text)


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)  # Permission name
    description = Column(String)
    scope = Column(Enum("organization", "team", name="permission_scope"), nullable=False, index=True)


class UserRole(Base):
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    role_name = Column(String)

    __table_args__ = (
        Index('idx_user_role_lookup', 'user_id', 'role_id', unique=True),
    )