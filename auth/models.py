from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.pg_connection import Base
from enum import Enum


class TokenType(Enum):
    JWT = "jwt"
    PASETO = "paseto"


class AuthType(Enum):
    LOCAL = "local"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    auth_type = Column(SQLAlchemyEnum(AuthType), default=AuthType.LOCAL)
    verified = Column(Boolean, default=False)

    refresh_tokens = relationship("RefreshToken", back_populates="user", foreign_keys="[RefreshToken.user_id]")
    organization_users = relationship("OrganizationUser", back_populates="user", cascade="all, delete-orphan")
    team_members = relationship("TeamMember", back_populates="user")
    user_roles = relationship("UserRole", back_populates="user")

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(String, index=True)
    expires_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    revoked = Column(Boolean, default=False)
    token_type = Column(SQLAlchemyEnum(TokenType), default=TokenType.JWT)
    nonce = Column(String, nullable=True)

    user = relationship("User", back_populates="refresh_tokens", foreign_keys=[user_id])
