import json
import secrets
from datetime import timedelta, datetime
from pyseto import Key, encode, decode
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from utils.custom_logger import logger
from auth.models import RefreshToken, TokenType
from auth.strategies.base_auth import BaseAuth

class PasetoAuth(BaseAuth):
    async def create_access_token(self, data: dict, expires_delta: timedelta):
        """
        Asynchronously creates an access token using the PASETO (Platform-Agnostic Security Tokens) standard.

        Parameters:
        - data (dict): A dictionary containing the payload data to be included in the token.
        - expires_delta (timedelta): A timedelta object representing the duration after which the token will expire.

        Returns:
        - str: A string representing the encoded access token.

        Raises:
        - Any exceptions related to key creation or token encoding will be propagated.
        """
        key = Key.new(version=2, key=settings.paseto_private_key, type="public")
        expire = datetime.utcnow() + expires_delta
        data.update({"exp": expire.isoformat()})
        token = encode(key, json.dumps(data)).decode('utf-8')
        return token

    async def create_refresh_token(self, data: dict, expires_delta: timedelta, db: AsyncSession):
        """
        Asynchronously creates a refresh token for a user and stores it in the database.

        Parameters:
        - data (dict): A dictionary containing user data, including the subject ('sub') which is the user's email.
        - expires_delta (timedelta): The time duration after which the token will expire.
        - db (AsyncSession): The asynchronous database session used to add and commit the refresh token.

        Returns:
        - str: The generated refresh token as a string.

        Raises:
        - Any exceptions related to database operations or encoding issues may be raised during the execution.
        """
        key = Key.new(version=2, type="public", key=settings.paseto_private_key)
        nonce = secrets.token_hex(32)
        data.update({"nonce": nonce})
        token = encode(key, json.dumps(data)).decode('utf-8')
        db_refresh_token = RefreshToken(
            user_email=data["sub"],
            token=token,
            token_type=TokenType(settings.auth_mode),
            nonce=nonce,
            expires_at=datetime.utcnow() + expires_delta,
            revoked=False
        )
        db.add(db_refresh_token)
        await db.commit()
        return token

    async def verify_token(self, token: str):
        """
        Verifies a given token using a public key and checks its expiration.

        Parameters:
        - token (str): The token string that needs to be verified.
        - db (AsyncSession): The asynchronous database session, though not used in the current implementation.

        Returns:
        - dict: A dictionary containing the decoded payload if the token is valid and not expired.
        - None: If the token is invalid or expired.

        Raises:
        - Exception: Logs an error and returns None if token verification fails for any reason.
        """
        try:
            key = Key.new(version=2, type="public", key=settings.paseto_public_key)
            payload = decode(key, token)
            payload_json = json.loads(payload.payload.decode('utf-8'))
            if "exp" in payload_json:
                exp = datetime.fromisoformat(payload_json["exp"])
                if exp < datetime.utcnow():
                    logger.error("Token has expired.")
                    return None
            return payload_json
        except Exception:
            logger.error(f"Token verification for {settings.auth_mode} failed!")
            return None
