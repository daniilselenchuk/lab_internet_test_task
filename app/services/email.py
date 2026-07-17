import logging
import os
from email.message import EmailMessage
import aiosmtplib

from app.schemas.contact import ContactRequest


logger = logging.getLogger("app.requests.email")


class EmailDeliveryError(Exception):
    pass


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EmailDeliveryError("Email service is not configured.")
    return value


async def send_contact_emails(contact: ContactRequest) -> None:
    try:
        host = _required_env("SMTP_HOST")
        sender = _required_env("SMTP_FROM_EMAIL")
        owner = _required_env("CONTACT_OWNER_EMAIL")
        port = int(os.getenv("SMTP_PORT", "587"))
        timeout = float(os.getenv("SMTP_TIMEOUT", "10"))
    except (EmailDeliveryError, ValueError):
        logger.error("email_configuration_invalid")
        raise EmailDeliveryError("Email service is not configured.") from None

    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
    if bool(username) != bool(password):
        logger.error("email_configuration_invalid")
        raise EmailDeliveryError("Email service is not configured.")

    owner_message = EmailMessage()
    owner_message["Subject"] = "Новое обращение с сайта"
    owner_message["From"] = sender
    owner_message["To"] = owner
    owner_message["Reply-To"] = contact.email
    owner_message.set_content(
        f"Имя: {contact.name}\n"
        f"Телефон: {contact.phone}\n"
        f"Email: {contact.email}\n\n"
        f"Комментарий:\n{contact.comment}"
    )

    user_message = EmailMessage()
    user_message["Subject"] = "Мы получили ваше обращение"
    user_message["From"] = sender
    user_message["To"] = contact.email
    user_message.set_content(
        f"Здравствуйте, {contact.name}!\n\n"
        "Спасибо за обращение. Мы получили ваше сообщение и скоро свяжемся с вами.\n\n"
        f"Ваше сообщение:\n{contact.comment}"
    )

    try:
        smtp_client = aiosmtplib.SMTP(
            hostname=host,
            port=port,
            username=username,
            password=password,
            start_tls=use_tls,
            timeout=timeout,
        )
        async with smtp_client:
            await smtp_client.send_message(owner_message)
            await smtp_client.send_message(user_message)
    except (OSError, aiosmtplib.SMTPException) as error:
        logger.error("email_delivery_failed error_type=%s", type(error).__name__)
        raise EmailDeliveryError("Email delivery failed.") from error
