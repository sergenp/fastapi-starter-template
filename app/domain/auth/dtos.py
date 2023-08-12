from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr


class TokenDto(BaseModel):
    access_token: str
    refresh_token: str


class LoginPayload(BaseModel):
    username: str
    password: str


class RegisterPayload(BaseModel):
    username: str
    email: str
    password: str


class RefreshTokenPayload(BaseModel):
    refresh_token: str


class UserDto(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserWithPasswordDto(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserProfileDto(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    birthday: date | None
    model_config = ConfigDict(from_attributes=True)


class UserWithProfileDto(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    profile: UserProfileDto | None
    model_config = ConfigDict(from_attributes=True)
