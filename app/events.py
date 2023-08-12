from pydantic import BaseModel, EmailStr, HttpUrl


class ConfirmationEmailEvent(BaseModel):
    base_url: HttpUrl
    email: EmailStr
    username: str
