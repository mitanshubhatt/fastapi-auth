from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from jose import jwt, JWTError
from datetime import datetime
from sqlalchemy import update
from pydantic import ValidationError

from db.connection import get_db
from config.settings import settings
from auth.models import User, RefreshToken
from auth.schemas import UserCreate, UserRead, Token
from auth.utils import get_password_hash, create_access_token, create_refresh_token, authenticate_user
from auth.dependencies import get_current_user

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Endpoint for registering new user

    Args:
        user (UserCreate): User details
        db (AsyncSession, optional)

    Raises:
        HTTPException: User already registered.
        HTTPException: Password and Email Validation Error.

    Returns:
        UserRead: User details except password
    """
    try:
        user_in_db = await db.execute(select(User).where(User.email == user.email))
        user_in_db = user_in_db.scalars().first()

        if user_in_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered."
            )

        hashed_password = await get_password_hash(user.password)
        db_user = User(
            full_name=user.full_name,
            email=user.email,
            hashed_password=hashed_password,
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except ValidationError as e:
        # Handle validation errors from Pydantic
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Endpoint for login

    Args:
        form_data (OAuth2PasswordRequestForm, optional): User creds
        db (AsyncSession, optional)

    Raises:
        HTTPException: Authentication Error

    Returns:
        Token: Token details
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = await create_refresh_token(
        data={"sub": form_data.username}, expires_delta=refresh_token_expires, db=db
    )
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Generate refresh token

    Args:
        refresh_token (str)
        db (AsyncSession, optional)

    Raises:
        credentials_exception: Unauthorized

    Returns:
        Token: Token Details
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        # Check token in database
        token_result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token, RefreshToken.revoked == False)
        )
        stored_token = token_result.scalars().first()
        if not stored_token or stored_token.expires_at < datetime.utcnow():
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/revoke-token")
async def revoke_refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    update_statement = (
        update(RefreshToken)
        .where(RefreshToken.token == refresh_token)
        .values(revoked=True)
    )
    await db.execute(update_statement)
    await db.commit()
    return {"message": "Token revoked successfully"}