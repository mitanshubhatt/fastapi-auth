import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
from utils.custom_logger import logger
from config.settings import settings

async def send_mail(email: str, subject: str, body_html: str):
    """
    Send an email using the NETCORE SMTP transporter.

    Args:
        email (str): Recipient's email address.
        subject (str): Email subject.
        body_html (str): HTML content of the email.

    Returns:
        dict: Details of the email sending status (accepted, rejected, response).
    """
    try:
        logger.info(f"Sending Email via NETCORE SMTP to: {email}, Subject: {subject}")

        # Parse NETCORE SMTP configuration from the URL
        smtp_url = urlparse(settings.smtp_netcore)
        smtp_host = smtp_url.hostname
        smtp_port = smtp_url.port
        smtp_username = smtp_url.username
        smtp_password = smtp_url.password
        # logger.info(f"host: {smtp_host}, {smtp_port}, {smtp_username}, {smtp_password}")
        use_tls = smtp_url.query == "secure=true"  # Check if 'secure=true' is in the query

        msg = MIMEMultipart()
        msg['From'] = settings.smtp_from_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if use_tls:
                server.starttls()
            server.login(smtp_username, smtp_password)

            response = server.sendmail(msg['From'], email, msg.as_string())
            logger.info(f"Email sent to {email} successfully via NETCORE SMTP.")

            return {
                "accepted": [email],
                "rejected": [],
                "response": response,
            }

    except Exception as e:
        logger.error(f"Failed to send email to {email} via NETCORE SMTP: {e}")
        return {
            "accepted": [],
            "rejected": [email],
            "response": str(e),
        }
