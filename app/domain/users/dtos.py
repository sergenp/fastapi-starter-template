from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LocationBase(BaseModel):
    latitude: Decimal = Field(ge=-90, le=90, decimal_places=6)
    longitude: Decimal = Field(ge=-180, le=180, decimal_places=6)


class LocationDto(LocationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserProfileBase(BaseModel):
    first_name: str | None
    last_name: str | None
    birthday: date | None


class UserProfileDto(UserProfileBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserDto(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserWithProfileDto(UserDto):
    profile: UserProfileDto | None = None
    model_config = ConfigDict(from_attributes=True)


class UserWithDistanceDto(UserDto):
    profile: UserProfileDto | None = None
    distance: float
    model_config = ConfigDict(from_attributes=True)
