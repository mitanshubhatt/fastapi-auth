from datetime import datetime, timedelta
from jose import jwt
from config.settings import settings
from utils.custom_logger import logger
from auth.models import RefreshToken, TokenType
from sqlalchemy.ext.asyncio import AsyncSession
from utils.base_auth import BaseAuth

class JWTAuth(BaseAuth):
    async def create_access_token(self, data: dict, expires_delta: timedelta):
        """
        Creates a JSON Web Token (JWT) for access control.

        Parameters:
        - data (dict): A dictionary containing the payload data to be encoded in the token.
        - expires_delta (timedelta): A timedelta object representing the duration until the token expires.

        Returns:
        - str: The encoded JWT as a string.

        Raises:
        - jwt.exceptions.PyJWTError: If there is an error in encoding the JWT.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire.isoformat()})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    async def create_refresh_token(self, data: dict, expires_delta: timedelta, db: AsyncSession):
        """
        Creates a new refresh token and stores it in the database.

        Parameters:
        - data (dict): A dictionary containing the payload for the token, typically including user information.
        - expires_delta (timedelta): The duration after which the token will expire.
        - db (AsyncSession): The asynchronous database session used to commit the new token to the database.

        Returns:
        - str: The encoded JWT refresh token.

        Raises:
        - jwt.PyJWTError: If there is an error encoding the JWT token.
        - sqlalchemy.exc.SQLAlchemyError: If there is an error committing the token to the database.
        """
        expire = datetime.utcnow() + expires_delta
        token = jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
        db_refresh_token = RefreshToken(
            user_email=data["sub"],
            token=token,
            token_type=TokenType(settings.auth_mode),
            nonce=None,
            expires_at=expire,
            revoked=False
        )
        db.add(db_refresh_token)
        await db.commit()
        return token

    async def verify_token(self, token: str):
        """
        Verifies a JWT token and returns its payload if valid.

        Parameters:
        token (str): The JWT token to be verified.

        Returns:
        dict or None: Returns the payload of the token as a dictionary if the token is valid and not expired.
                      Returns None if the token is invalid or expired.

        Raises:
        jwt.JWTError: If there is an error decoding the token.
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            if "exp" in payload:
                exp = datetime.fromisoformat(payload["exp"])
                if exp < datetime.utcnow():
                    logger.error("Token has expired.")
                    return None
            return payload
        except jwt.JWTError:
            return None
