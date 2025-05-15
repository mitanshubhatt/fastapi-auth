from sqlalchemy import Integer, Column, String, Index, ForeignKey, Enum, Text

from db.pg_connection import Base


class UserRole(Base):
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    role_name = Column(String)

    __table_args__ = (
        Index('idx_user_role_lookup', 'user_id', 'role_id', unique=True),
    )


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    scope = Column(Enum("organization", "team", name="role_scope"), nullable=False, index=True)
    slug = Column(String, index=True, unique=True)

    permissions_cache = Column(Text)