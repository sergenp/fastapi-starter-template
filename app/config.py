from typing import Any, List, Union

from pydantic import AnyHttpUrl, FieldValidationInfo, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    TEST_POSTGRES_DB: str
    DATABASE_URI: PostgresDsn | None = None
    TEST_DATABASE_URI: PostgresDsn | None = None
    API_V1_STR: str = "api/v1"

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: str | None, values: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        values = values.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )

    @field_validator("TEST_DATABASE_URI", mode="before")
    def assemble_test_db_connection(cls, v: str | None, values: FieldValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        values = values.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"{values.get('TEST_POSTGRES_DB') or ''}",
        )

    # JWT Configs
    JWT_EMAIL_SECRET_KEY: str
    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EMAIL_TOKEN_EXPIRE_MINUTES: str
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: str
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: str

    # MINIO Configs
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_HOSTNAME: str
    MINIO_PORT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_STORAGE_USE_HTTPS: bool
    MINIO_MAX_UPLOAD_SIZE: int

    # EMAIL CONFIGS
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_PORT: int
    EMAIL_SERVER: str
    EMAIL_STARTTLS: bool = False
    EMAIL_SSL_TLS: bool = True
    EMAIL_USE_CREDENTIALS: bool = True
    EMAIL_VALIDATE_CERTS: bool = True
    EMAIL_SUPRESS_SEND: bool = False

    # Max amount of results per api call
    MAX_PAGE_SIZE: int = 100
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
