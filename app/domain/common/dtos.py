from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr


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
    profile: UserProfileDto | None = None
    model_config = ConfigDict(from_attributes=True)
