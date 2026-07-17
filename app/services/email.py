import logging
from email.message import EmailMessage

import aiosmtplib

from pydantic import ValidationError
from app.config import get_settings
from app.schemas.contact import ContactRequest


logger = logging.getLogger("app.requests.email")


class EmailDeliveryError(Exception):
    pass


async def send_contact_emails(contact: ContactRequest) -> None:
    try:
        settings = get_settings()
    except ValidationError as error:
        issues = ",".join(
            f"{'.'.join(map(str, issue['loc']))}:{issue['type']}"
            for issue in error.errors()
        )
        logger.error("email_configuration_invalid issues=%s", issues)
        raise EmailDeliveryError("Email service is not configured.") from None

    password = (
        settings.smtp_password.get_secret_value()
        if settings.smtp_password
        else None
    )
    has_incomplete_auth = bool(settings.smtp_username) != bool(password)
    missing_fields = [
        name
        for name, value in (
            ("SMTP_HOST", settings.smtp_host),
            ("SMTP_FROM_EMAIL", settings.smtp_from_email),
            ("CONTACT_OWNER_EMAIL", settings.contact_owner_email),
        )
        if not value
    ]

    if has_incomplete_auth or missing_fields:
        logger.error(
            "email_configuration_invalid missing_fields=%s incomplete_auth=%s",
            ",".join(missing_fields) or "none",
            has_incomplete_auth,
        )
        raise EmailDeliveryError("Email service is not configured.")

    sender = str(settings.smtp_from_email)
    owner = str(settings.contact_owner_email)
    contact_details = (
        f"Имя: {contact.name}\n"
        f"Телефон: {contact.phone}\n"
        f"Email: {contact.email}\n\n"
        f"Комментарий:\n{contact.comment}"
    )

    owner_message = EmailMessage()
    owner_message["Subject"] = "Новое обращение с сайта"
    owner_message["From"] = sender
    owner_message["To"] = owner
    owner_message["Reply-To"] = contact.email
    owner_message.set_content(
        "Получено новое обращение через форму на сайте.\n\n"
        f"{contact_details}\n\n"
        "Чтобы ответить пользователю, ответьте на это письмо."
    )

    user_message = EmailMessage()
    user_message["Subject"] = "Копия вашего обращения"
    user_message["From"] = sender
    user_message["To"] = contact.email
    user_message.set_content(
        f"Здравствуйте, {contact.name}!\n\n"
        "Спасибо за обращение. Мы получили ваше сообщение и скоро свяжемся с вами.\n\n"
        "Копия вашего обращения:\n\n"
        f"{contact_details}"
    )

    stage = "connect"
    logger.info(
        "email_delivery_started smtp_host=%s smtp_port=%s start_tls=%s auth=%s",
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_use_tls,
        bool(settings.smtp_username),
    )

    try:
        smtp_client = aiosmtplib.SMTP(
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=password,
            start_tls=settings.smtp_use_tls,
            timeout=settings.smtp_timeout,
        )
        async with smtp_client:
            logger.info("email_smtp_connected")
            stage = "owner_message"
            await smtp_client.send_message(owner_message)
            logger.info("email_owner_notification_sent")
            stage = "user_message"
            await smtp_client.send_message(user_message)
            logger.info("email_user_confirmation_sent")
    except (OSError, aiosmtplib.SMTPException) as error:
        cause_type = type(error.__cause__).__name__ if error.__cause__ else "none"
        logger.error(
            "email_delivery_failed stage=%s error_type=%s cause_type=%s smtp_code=%s",
            stage,
            type(error).__name__,
            cause_type,
            getattr(error, "code", "none"),
        )
        raise EmailDeliveryError("Email delivery failed.") from error
