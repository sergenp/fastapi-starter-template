from fastapi import Depends, HTTPException, status
from sqlalchemy import or_, select, true, update
from sqlalchemy.orm import joinedload

from app.domain.auth.dtos import (
    RegisterPayload,
    UserDto,
    UserWithPasswordDto,
    UserWithProfileDto,
)
from app.infrastructure.services.session_service import SessionMaker
from app.repositories.users.models import User, UserProfile


class UserService:
    def __init__(self, _session: SessionMaker = Depends(SessionMaker)) -> None:
        self._session = _session

    async def get_user_with_id(self, user_id: int) -> UserWithProfileDto:
        async with self._session as session:
            query = select(User).filter(User.id == user_id).options(joinedload(User.profile))
            result = await session.scalar(query)
            if not result:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found.")

        return UserWithProfileDto.model_validate(result)

    async def get_user_with_username(self, username: str) -> UserWithPasswordDto:
        async with self._session as session:
            query = select(User).filter(User.username == username)
            result = await session.scalar(query)
            if not result:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found.")

        return UserWithPasswordDto.model_validate(result)

    async def activate_user(self, username: str, is_active: bool) -> bool:
        async with self._session as session:
            query = (
                update(User)
                .filter(User.username == username)
                .values({"is_active": is_active})
                .returning(User.is_active)
            )
            result = await session.scalar(query)
            if not result:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail="Couldn't activate user, user not found",
                )

        return result

    async def is_user_exists(self, username: str, email: str) -> bool:
        async with self._session as session:
            query = select(User).filter(
                or_(
                    User.email == email,
                    User.username == username,
                )
            )
            result = await session.scalar(query)

        return bool(result)

    async def is_user_active(self, username: str, email: str) -> bool:
        async with self._session as session:
            query = select(User).filter(
                or_(
                    User.email == email,
                    User.username == username,
                ),
                User.is_active == true(),
            )
            result = await session.scalar(query)

        return bool(result)

    async def create_user(self, register_payload: RegisterPayload) -> UserDto:
        async with self._session as session:
            user = User(**register_payload.model_dump())
            user.profile = UserProfile()
            session.add(user)
            await session.commit()

        return UserDto.model_validate(user)
