from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from db.connection import get_db
from auth.model import User
from auth.schema import UserCreate


router = APIRouter(prefix="/user")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_in_db = await db.execute(select(User).where(User.username == user.username))
    user_in_db = user_in_db.scalars().first()

    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
