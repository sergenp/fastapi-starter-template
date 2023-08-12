from fastapi import Depends, HTTPException
from sqlalchemy import VARCHAR, and_, func, not_, select
from sqlalchemy.orm import joinedload, with_expression
from sqlalchemy.sql.expression import cast

from app.domain.common.util import GeoLocationHelper
from app.domain.users.dtos import (
    LocationDto,
    UserProfileBase,
    UserProfileDto,
    UserWithDistanceDto,
    UserWithProfileDto,
)
from app.infrastructure.dtos import PaginationDto
from app.infrastructure.services.paginator import Paginator
from app.infrastructure.services.session_service import SessionMaker
from app.repositories.users.models import User, UserLocation, UserProfile


class UserService:
    def __init__(self, _session: SessionMaker = Depends(SessionMaker)) -> None:
        self._session = _session

    async def get_users_within_distance(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 100,
        distance: int = 100,
    ) -> PaginationDto[UserWithDistanceDto]:
        async with self._session as session:
            user_location = select(UserLocation).join(User).where(User.id == user_id)
            user_location = await session.scalar(user_location)
            if not user_location:
                raise HTTPException(404, detail="User doesn't have a location")

            lat = user_location.latitude
            lon = user_location.longitude

            lat_min, lat_max, lon_min, lon_max = GeoLocationHelper.calculate_bounding_box(
                lat, lon, distance
            )

            distance_q = (
                func.acos(
                    func.sin(func.radians(lat)) * func.sin(func.radians(UserLocation.latitude))
                    + func.cos(func.radians(lat))
                    * func.cos(func.radians(UserLocation.latitude))
                    * func.cos(func.radians(lon) - func.radians(UserLocation.longitude))
                )
                * 6371
            ).label("distance")

            query = (
                select(User)
                .join(UserLocation, isouter=False)
                .where(
                    not_(
                        and_(
                            cast(UserLocation.latitude, VARCHAR) == str(lat),
                            cast(UserLocation.longitude, VARCHAR) == str(lon),
                        )
                    ),
                    and_(
                        UserLocation.latitude.between(lat_min, lat_max),
                        UserLocation.longitude.between(lon_min, lon_max),
                        distance_q < distance,
                    ),
                )
                .order_by(distance_q)
                .options(joinedload(User.profile), with_expression(User.distance, distance_q))
            )

            return await Paginator.get_paginated_response(
                session, query, limit=limit, page=page, serializer=UserWithDistanceDto
            )

    async def get_user_with_id(self, user_id: int) -> UserWithProfileDto:
        async with self._session as session:
            query = select(User).filter(User.id == user_id).options(joinedload(User.profile))
            result = await session.scalar(query)
            if not result:
                raise HTTPException(404)

        return UserWithProfileDto.model_validate(result)

    async def update_user_profile(
        self, user: UserWithProfileDto, new_profile: UserProfileBase
    ) -> UserProfileDto:
        query = select(UserProfile).join(User).where(User.id == user.id)
        async with self._session as session:
            profile = await session.scalar(query)
            profile.first_name = new_profile.first_name
            profile.last_name = new_profile.last_name
            profile.birthday = new_profile.birthday
            await session.commit()
        return UserProfileDto.model_validate(profile)

    async def update_user_location(
        self, user: UserWithProfileDto, location: LocationDto
    ) -> LocationDto:
        query = select(User).where(User.id == user.id).options(joinedload(User.location))
        async with self._session as session:
            user = await session.scalar(query)
            if not user.location:
                user.location = UserLocation(**location.model_dump(), user_id=user.id)
            else:
                user.location.longitude = location.longitude
                user.location.latitude = location.latitude
            await session.commit()
        return LocationDto(
            id=user.location.id,
            latitude=user.location.latitude,
            longitude=user.location.longitude,
        )
