from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.domain.auth.dtos import (
    LoginPayload,
    RefreshTokenPayload,
    RegisterPayload,
    TokenDto,
    UserWithProfileDto,
)
from app.domain.auth.services.auth_service import AuthService
from app.domain.common.services.token_decode_service import TokenDecodeService

router = APIRouter()


@router.get("/me/")
async def get_me(
    user: Annotated[UserWithProfileDto, Depends(TokenDecodeService())],
) -> UserWithProfileDto:
    return user


@router.post("/login/")
async def login(
    login_payload: LoginPayload,
    service: AuthService = Depends(AuthService),
) -> TokenDto:
    return await service.login(login_payload)


@router.get("/confirm-email/{token}/")
async def confirm_email(
    token: str,
    service: AuthService = Depends(AuthService),
) -> bool:
    # TODO Add a token blacklist logic
    # i.e. invalidate email token after it is used one time
    return await service.confirm_email(token)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(
    register_payload: RegisterPayload,
    service: AuthService = Depends(AuthService),
) -> TokenDto:
    return await service.register(register_payload)


@router.post("/refresh-token/", status_code=status.HTTP_201_CREATED)
async def refresh_token(
    refresh_token_payload: RefreshTokenPayload,
    service: AuthService = Depends(AuthService),
) -> TokenDto:
    return service.refresh_token(refresh_token_payload.refresh_token)
