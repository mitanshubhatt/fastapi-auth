import time

from sqlalchemy import Integer, Column, String, Index, ForeignKey

from db.pg_connection import Base


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