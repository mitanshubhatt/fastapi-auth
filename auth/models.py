from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from db.connection import Base
from enum import Enum


class TokenType(Enum):
    JWT = "jwt"
    PASETO = "paseto"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", foreign_keys="[RefreshToken.user_email]")
    organization_users = relationship("OrganizationUser", back_populates="user")  # Ensure this line is correct
    team_members = relationship("TeamMember", back_populates="user")

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey('users.email'))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow())
    revoked = Column(Boolean, default=False)
    token_type = Column(SQLAlchemyEnum(TokenType), default=TokenType.JWT)
    nonce = Column(String, nullable=True)

    user = relationship("User", back_populates="refresh_tokens", foreign_keys=[user_email])
