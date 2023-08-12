import asyncio

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.config import settings


class EmailService:
    def __init__(self) -> None:
        config = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_SERVER,
            MAIL_SSL_TLS=settings.EMAIL_SSL_TLS,
            MAIL_STARTTLS=settings.EMAIL_STARTTLS,
            USE_CREDENTIALS=settings.EMAIL_USE_CREDENTIALS,
            VALIDATE_CERTS=settings.EMAIL_VALIDATE_CERTS,
            SUPPRESS_SEND=settings.EMAIL_SUPRESS_SEND,
            TEMPLATE_FOLDER="app/templates",
        )
        self._fm = FastMail(config)

    async def send_email(self, template_name: str, email_to: str, subject: str, **template_data):
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            template_body=template_data,
            subtype="html",
        )
        asyncio.create_task(self._fm.send_message(message, template_name=template_name))
