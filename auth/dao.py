from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from auth.models import User
from utils.encryption import DataEncryptor  # Assuming DataEncryptor is in utils


class UserDAO:
    def __init__(self, db: AsyncSession, encryptor: Optional[DataEncryptor] = None):
        self.encryptor = encryptor
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Fetches a user by their ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, plain_email: str) -> Optional[User]:
        """
        Fetches a user by their PLAINTEXT email.
        The email will be encrypted before querying the database.
        """
        encrypted_email = await self.encryptor.encrypt(plain_email)
        result = await self.db.execute(select(User).where(User.email == encrypted_email))
        return result.scalars().first()

    async def get_user_by_encrypted_email(self, encrypted_email: str) -> Optional[User]:
        """
        Fetches a user by their ENCRYPTED email.
        """
        result = await self.db.execute(select(User).where(User.email == encrypted_email))
        return result.scalars().first()
