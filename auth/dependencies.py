from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.connection import get_db
from config.settings import settings
from auth.models import User
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = await settings.auth_instance.verify_token(token)
        if payload is None:
            logging.error("Token verification failed: Payload is None")
            raise credentials_exception

        email: str = payload.get("sub")
        if email is None:
            logging.error("Token verification failed: Email is None")
            raise credentials_exception

        user_result = await db.execute(select(User).where(User.email == email))
        user = user_result.scalars().first()
        if user is None:
            logging.error("User not found in database")
            raise credentials_exception

        return user

    except Exception as e:
        logging.error(f"Exception during token verification: {e}")
        raise credentials_exception from e
