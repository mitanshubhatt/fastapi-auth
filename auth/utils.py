# import aiofiles
import uuid
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import settings
from utils.custom_logger import logger
from auth.models import User
from datetime import timedelta
from urllib.parse import urljoin, urlencode
from utils.email_provider import send_mail
from html_templates.email_verification_template import email_verification_template
from html_templates.forgot_pass_template import reset_password_template

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()
    if not user or not await verify_password(password, user.hashed_password):
        return False
    return user


async def send_email_verification(redis_client, email, first_name, title):
    """
    Sends an email verification link to the specified email.

    Args:
        redis_client: Redis client for storing verification tokens.
        email: User's email address.
        first_name: User's first name.

    Raises:
        Exception: If there's an error sending the email.
    """
    try:
        # Generate a unique verification token
        verification_token = uuid.uuid4()
        token_key = f"{title}:{verification_token}"

        await redis_client.set(token_key, email, expire=timedelta(hours=3))

        verification_url = urljoin(
            settings.hinata_host,
            'auth/emailVerification'
        )
        query_params = urlencode({'code': verification_token})
        verification_link = f"https://{verification_url}?{query_params}"

        subject = f"Registration Confirmation"
        body_html = email_verification_template({
            "userName": first_name,
            "verifyLink": verification_link,
            "willExpireIn": 3 * 60
        })
        await send_mail(
            email=email,
            subject=subject,
            body_html=body_html
        )

        logger.info("Verification email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        raise e

async def send_forgot_password_email(redis_client, email, first_name, title):
    """
    Sends an email verification link to the specified email.

    Args:
        redis_client: Redis client for storing verification tokens.
        email: User's email address.
        first_name: User's first name.

    Raises:
        Exception: If there's an error sending the email.
    """
    try:
        # Generate a unique verification token
        verification_token = uuid.uuid4()
        token_key = f"{title}:{verification_token}"

        await redis_client.set(token_key, email, expire=timedelta(hours=3))

        verification_url = urljoin(
            settings.hinata_host,
            'auth/setPassword'
        )
        query_params = urlencode({'code': verification_token})
        verification_link = f"https://{verification_url}?{query_params}"

        subject = f"Registration Confirmation"
        body_html = reset_password_template({
            "userName": first_name,
            "verifyLink": verification_link,
            "willExpireIn": 3 * 60
        })
        await send_mail(
            email=email,
            subject=subject,
            body_html=body_html
        )

        logger.info("Verification email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        raise e