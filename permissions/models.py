from sqlalchemy import Integer, Column, String, Index, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from db.pg_connection import Base



class RolePermission(Base):
    __tablename__ = 'role_permission'

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey('permissions.id'), nullable=False, index=True)

    permission_name = Column(String)
    
    # Relationships
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    __table_args__ = (
        Index('idx_role_permission_unique', 'role_id', 'permission_id', unique=True),
    )


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    slug = Column(String, unique=True, index=True)
    scope = Column(Enum("organization", "team", name="permission_scope"), nullable=False, index=True)
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
