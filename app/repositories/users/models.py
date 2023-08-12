from sqlalchemy import Boolean, Column, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, query_expression, relationship

from app.repositories import Base


class UserLocation(Base):
    __tablename__ = "user_locations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    latitude = Column(Numeric(precision=8, scale=6), index=True)
    longitude = Column(Numeric(precision=9, scale=6), index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True, index=True
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=False)
    profile: Mapped["UserProfile"] = relationship(back_populates="user")
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id"), nullable=False, unique=True, index=True
    )
    location: Mapped["UserLocation"] = relationship()
    distance = query_expression()


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    birthday = Column(Date, nullable=True)
    user: Mapped["User"] = relationship(back_populates="profile")
