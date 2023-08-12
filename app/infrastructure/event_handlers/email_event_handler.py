from enum import StrEnum

from app.config import settings
from app.events import ConfirmationEmailEvent
from app.infrastructure.event_handlers.base_event_handler import BaseEventHandler
from app.infrastructure.services.email_service import EmailService
from app.infrastructure.services.mediator import Mediator


class EmailTemplate(StrEnum):
    PASSWORD_RESET = "password-reset.html"
    CONFIRMATION = "confirmation.html"


class ConfirmationEmailEventHandler(BaseEventHandler):
    async def handle(self, event: ConfirmationEmailEvent) -> None:
        from app.domain.auth.services.auth_service import AuthService, TokenTypes

        email_service = EmailService()
        token = AuthService._create_token(
            TokenTypes.EMAIL_CONFIRM, username=event.username, email=event.email
        )
        url = f"{event.base_url}{settings.API_V1_STR}/confirm-email/{token}/"
        await email_service.send_email(
            template_name=EmailTemplate.CONFIRMATION.value,
            email_to=event.email,
            subject="Confirmation Email - FastApi Starter Template",
            user=event.email,
            url=url,
        )


Mediator.register(ConfirmationEmailEvent, ConfirmationEmailEventHandler())
