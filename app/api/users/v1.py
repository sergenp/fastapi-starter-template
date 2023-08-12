from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.domain.common.services.token_decode_service import TokenDecodeService
from app.domain.users.dtos import (
    LocationBase,
    LocationDto,
    UserProfileBase,
    UserProfileDto,
    UserWithDistanceDto,
    UserWithProfileDto,
)
from app.domain.users.service import UserService
from app.infrastructure.dtos import PaginationDto

router = APIRouter(prefix="/users")


@router.get("/")
async def get_users(
    user: Annotated[UserWithProfileDto, Depends(TokenDecodeService())],
    service: UserService = Depends(UserService),
    page: int = Query(ge=0, default=1),
    limit: int = Query(ge=1, le=100, default=100),
    distance: int = Query(ge=0, le=100, default=100),
) -> PaginationDto[UserWithDistanceDto]:
    return await service.get_users_within_distance(
        user_id=user.id,
        page=page,
        limit=limit,
        distance=distance,
    )


@router.get("/{id}/")
async def get_user(
    id: int,
    service: UserService = Depends(UserService),
) -> UserWithProfileDto:
    return await service.get_user_with_id(id)


@router.put("/me/profile/", status_code=status.HTTP_201_CREATED)
async def update_user_profile(
    profile: UserProfileBase,
    user: Annotated[UserWithProfileDto, Depends(TokenDecodeService())],
    user_service: UserService = Depends(UserService),
) -> UserProfileDto:
    return await user_service.update_user_profile(user, profile)


@router.put("/{id}/location/", status_code=status.HTTP_201_CREATED)
async def update_user_location(
    location: LocationBase,
    user: Annotated[UserWithProfileDto, Depends(TokenDecodeService())],
    user_service: UserService = Depends(UserService),
) -> LocationDto:
    return await user_service.update_user_location(user, location)
