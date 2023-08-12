from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.domain.auth.services.auth_service import AuthService
from app.domain.common.dtos import UserWithProfileDto


class TokenDecodeService:
    async def __call__(
        self,
        authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        auth_service: AuthService = Depends(AuthService),
    ) -> UserWithProfileDto:
        credentials = authorization.credentials
        return await auth_service.get_user_from_token(credentials)
