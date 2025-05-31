import json
import uuid
from datetime import timedelta
from urllib.parse import urljoin

from config.settings import settings
from html_templates.invite_template import invitation_template
from utils.custom_logger import logger
from utils.email_provider import send_mail


async def send_invite_email(redis_client, email, organization_id: int, role_id: int, title):
    try:
        # Generate a unique verification token
        verification_token = uuid.uuid4()
        token_key = f"{title}:{verification_token}"

        value = {
            "email": email,
            "organization_id": organization_id,
            "role_id": role_id
        }

        await redis_client.set(token_key, json.dumps(value), expire=timedelta(hours=24))

        invitation_url = urljoin(
            settings.hinata_host,
            f'auth/signup?inviteCode=${verification_token}'
        )
        invitation_link = f"https://{invitation_url}"

        subject = f"Registration Confirmation"
        body_html = invitation_template({
            "verifyLink": invitation_link
        })
        await send_mail(
            email=email,
            subject=subject,
            body_html=body_html
        )

        logger.info("Invitation email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send invitation email: {e}")
        raise e
