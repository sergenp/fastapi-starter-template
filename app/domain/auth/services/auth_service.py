import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict

import jwt
from fastapi import Depends, HTTPException, Request, status
from passlib.hash import pbkdf2_sha256

from app.config import settings
from app.domain.auth.dtos import (
    LoginPayload,
    RegisterPayload,
    TokenDto,
    UserWithPasswordDto,
    UserWithProfileDto,
)
from app.events import ConfirmationEmailEvent
from app.infrastructure.services.mediator import Mediator
from app.infrastructure.services.session_service import SessionMaker

from .user_service import UserService


class TokenTypes(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_CONFIRM = "email_confirm"


class AuthService:
    token_type_settings_map: Dict[TokenTypes, str] = {
        TokenTypes.ACCESS: settings.JWT_ACCESS_SECRET_KEY,
        TokenTypes.REFRESH: settings.JWT_REFRESH_SECRET_KEY,
        TokenTypes.EMAIL_CONFIRM: settings.JWT_EMAIL_SECRET_KEY,
    }

    token_type_expire_time_map: Dict[TokenTypes, timedelta] = {
        TokenTypes.ACCESS: timedelta(hours=int(settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS)),
        TokenTypes.REFRESH: timedelta(days=int(settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)),
        TokenTypes.EMAIL_CONFIRM: timedelta(minutes=int(settings.JWT_EMAIL_TOKEN_EXPIRE_MINUTES)),
    }

    def __init__(
        self,
        _request: Request,
        _session: SessionMaker = Depends(SessionMaker),
        user_service: UserService = Depends(UserService),
    ) -> None:
        self._request = _request
        self._session: SessionMaker = _session
        self._user_service: UserService = user_service

    @staticmethod
    def decode_token(token: str, token_type: TokenTypes, **options) -> dict:
        secret_key = AuthService.token_type_settings_map[token_type]
        return jwt.decode(
            token,
            secret_key,
            options=options,
            algorithms=[settings.JWT_ALGORITHM],
        )

    @staticmethod
    def _create_token(token_type: TokenTypes, **extra_payload) -> str:
        key = AuthService.token_type_settings_map[token_type]
        expire_time = AuthService.token_type_expire_time_map[token_type]

        # expire date is now + expire time + random jitter to avoid issuing the same token
        exp_date = (
            datetime.utcnow() + expire_time + timedelta(milliseconds=int.from_bytes(os.urandom(2)))
        )
        payload = {"exp": exp_date, "iat": datetime.utcnow()}
        payload.update(**extra_payload)
        token = jwt.encode(
            payload=payload,
            key=key,
            algorithm=settings.JWT_ALGORITHM,
        )
        return token

    async def get_user_from_token(self, token: str) -> UserWithProfileDto:
        decoded = self.decode_token(token, token_type=TokenTypes.ACCESS)
        user = await self._user_service.get_user_with_id(decoded["id"])
        if not user.is_active:
            # TODO: Don't throw the HTTP exception from here,
            # throw something called "UserNotActiveException" or smt,
            # then map this domain error at app.exception
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User has not confirmed email"
            )
        return user

    def _create_token_payload(self, access_token=None, refresh_token=None, **payload) -> TokenDto:
        if access_token is None:
            access_token = self._create_token(token_type=TokenTypes.ACCESS, **payload)
        if refresh_token is None:
            refresh_token = self._create_token(token_type=TokenTypes.REFRESH, **payload)
        return TokenDto(access_token=access_token, refresh_token=refresh_token)

    async def login(self, login_data: LoginPayload) -> TokenDto:
        """
        Gets email and password, finds the matching user, and returns a JWT token
        """
        user_dto: UserWithPasswordDto = await self._user_service.get_user_with_username(
            login_data.username
        )

        if not pbkdf2_sha256.verify(login_data.password, user_dto.password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        # TODO: decide what payload to pass into the JWT, maybe user roles? permissions? email? etc.
        return self._create_token_payload(id=user_dto.id, email=user_dto.email)

    async def register(self, register_dto: RegisterPayload) -> TokenDto:
        is_user_exists = await self._user_service.is_user_exists(
            register_dto.username, register_dto.email
        )

        if is_user_exists:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Given email is already in use")

        register_dto.password = pbkdf2_sha256.hash(register_dto.password)

        user = await self._user_service.create_user(register_dto)
        await Mediator.send(
            ConfirmationEmailEvent(
                email=user.email,
                username=user.username,
                base_url=str(self._request.base_url),
            )
        )

        return self._create_token_payload(id=user.id, email=user.email)

    async def confirm_email(self, confirm_token: str) -> bool:
        try:
            # if the token is valid, activate user
            decoded = self.decode_token(confirm_token, TokenTypes.EMAIL_CONFIRM)
            return await self._user_service.activate_user(
                username=decoded["username"], is_active=True
            )
        except jwt.ExpiredSignatureError:
            # resend the email if token is expired,
            # if token is invalid, invalid token exception is caught by exception handling
            # see app.exceptions
            decoded = self.decode_token(confirm_token, TokenTypes.EMAIL_CONFIRM, verify_exp=False)
            username, email = decoded["username"], decoded["email"]
            await Mediator.send(
                ConfirmationEmailEvent(
                    email=email,
                    username=username,
                    base_url=str(self._request.base_url),
                )
            )
            # TODO raise custom error
            raise

    def refresh_token(self, refresh_token: str) -> TokenDto:
        """
        Creates a new access token from a refresh token
        """
        payload = self.decode_token(refresh_token, TokenTypes.REFRESH)
        # TODO: decide what payload to pass into the JWT, maybe user roles? permissions? email? etc.
        # create a new access token for the given refresh token, do not recreate the refresh token
        return self._create_token_payload(
            id=payload["id"], email=payload["email"], refresh_token=refresh_token
        )
