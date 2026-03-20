"""Email tools module for DeckSmith."""

import logging
import os
import re
import smtplib
from email.mime.text import MIMEText
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

EMAIL_HOST_USER: Optional[str] = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD: Optional[str] = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_HOST: Optional[str] = os.getenv("EMAIL_HOST")
EMAIL_PORT: Optional[str] = os.getenv("EMAIL_PORT")
EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@decksmith.app")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class EmailValidationError(Exception):
    """Exception raised for email validation errors."""
    pass


class EmailSendError(Exception):
    """Exception raised when email sending fails."""
    pass


def validate_email(email: str) -> bool:
    """Validate email format using regex.

    Args:
        email: The email address to validate.

    Returns:
        True if email format is valid, False otherwise.
    """
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def sanitize_subject(subject: str) -> str:
    """Sanitize email subject line by removing newlines and control characters.

    Args:
        subject: The email subject to sanitize.

    Returns:
        A sanitized subject string.
    """
    if not subject:
        return ""
    subject = re.sub(r'[\r\n\x00-\x1f\x7f-\x9f]', ' ', subject)
    return subject.strip()[:255]


def sanitize_body(body: str) -> str:
    """Sanitize email body content.

    Args:
        body: The email body to sanitize.

    Returns:
        A sanitized body string.
    """
    if not body:
        return ""
    body = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', body)
    return body


def send_email(subject: str, body: str, to_email: str) -> bool:
    """Send an email with proper validation and error handling.

    Args:
        subject: The email subject line.
        body: The email body content.
        to_email: The recipient email address.

    Returns:
        True if email was sent successfully.

    Raises:
        EmailValidationError: If email validation fails.
        EmailSendError: If email sending fails.
    """
    if not validate_email(to_email):
        logger.error("Invalid email address: %s", to_email)
        raise EmailValidationError(f"Invalid email address: {to_email}")

    if not EMAIL_HOST or not EMAIL_PORT:
        logger.error("Email server not configured")
        raise EmailSendError("Email server not configured")

    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        logger.error("Email credentials not configured")
        raise EmailSendError("Email credentials not configured")

    subject = sanitize_subject(subject)
    body = sanitize_body(body)
    to_email = to_email.strip()

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL(EMAIL_HOST, int(EMAIL_PORT), timeout=30) as server:
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        logger.info("Email sent successfully to %s", to_email)
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP authentication failed: %s", e)
        raise EmailSendError("Email authentication failed") from e
    except smtplib.SMTPException as e:
        logger.error("SMTP error while sending email: %s", e)
        raise EmailSendError(f"Failed to send email: {e}") from e
    except Exception as e:
        logger.error("Unexpected error sending email: %s", e)
        raise EmailSendError(f"Unexpected error: {e}") from e


tools = {
    "send_email": send_email
}


def use_tool(tool_name: str, *args) -> Optional[bool]:
    """Execute a registered tool by name.

    Args:
        tool_name: The name of the tool to execute.
        *args: Arguments to pass to the tool.

    Returns:
        The result of the tool execution, or None if tool not found.
    """
    if tool_name in tools:
        try:
            return tools[tool_name](*args)
        except (EmailValidationError, EmailSendError) as e:
            logger.error("Tool %s failed: %s", tool_name, e)
            raise
    else:
        logger.warning("Tool not found: %s", tool_name)
        return None
