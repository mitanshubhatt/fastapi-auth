from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    refresh_tokens = relationship("RefreshToken", back_populates="user", foreign_keys="[RefreshToken.user_email]")

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, ForeignKey('users.email'))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow())
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="refresh_tokens", foreign_keys=[user_email])

