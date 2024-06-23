import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.future import select
from config.settings import settings
from auth.models import User, RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password):
    return pwd_context.hash(password)

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def create_refresh_token(data: dict, expires_delta: timedelta, db: AsyncSession):
    expire = datetime.utcnow() + expires_delta
    nonce = os.urandom(16).hex()
    current_time = datetime.utcnow()
    extended_data = {
        **data,
        "iat": current_time,
        "nonce": nonce,
    }
    token = jwt.encode(extended_data, settings.secret_key, algorithm=settings.algorithm)
    db_refresh_token = RefreshToken(
        user_email=data["sub"],
        token=token,
        expires_at=expire,
        revoked=False
    )
    db.add(db_refresh_token)
    await db.commit()
    return token

async def authenticate_user(db, email: str, password: str):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user
