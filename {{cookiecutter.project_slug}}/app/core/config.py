import os
import random
import secrets
from typing import Any, List, Optional, Union

from dotenv import load_dotenv
from pydantic import (
    AnyHttpUrl,
    EmailStr,
    PostgresDsn,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def is_running_in_docker() -> bool:
    """Verify if the application is running in a Docker container.

    Raises:
        ValueError: Unable to verify if the application is running in a Docker container.

    Returns:
        bool: True if the application is running in a Docker container.
    """
    if os.environ.get("SERVER_ENVIROMENT", "production") == "production":
        return True
    return os.path.exists("/.dockerenv")


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 100000
    SERVER_HOST: AnyHttpUrl
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_DB_TEST: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SQLALCHEMY_DATABASE_URI_TEST: Optional[PostgresDsn] = None
    REDIS_HOST: str
    RATE_LIMIT_TIME: Optional[str] = "1000/minute"

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        user = info.data.get("POSTGRES_USER")
        password = info.data.get("POSTGRES_PASSWORD")
        if is_running_in_docker():
            host = info.data.get("POSTGRES_SERVER")
        else:
            host = "localhost"
        db = info.data.get("POSTGRES_DB")

        if all([user, password, host, db]):
            return f"postgresql://{user}:{password}@{host}/{db}"
        else:
            return None

    @field_validator("SQLALCHEMY_DATABASE_URI_TEST", mode="before")
    @classmethod
    def assemble_db_connection_test(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        user = info.data.get("POSTGRES_USER")
        password = info.data.get("POSTGRES_PASSWORD")

        if is_running_in_docker():
            host = info.data.get("POSTGRES_SERVER")
        else:
            host = "localhost"
        db = info.data.get("POSTGRES_DB_TEST")
        if all([user, password, host, db]):
            return f"postgresql://{user}:{password}@{host}/{db}"
        else:
            return None

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME", mode="before")
    @classmethod
    def get_project_name(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v:
            return info.data.get("PROJECT_NAME")
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @field_validator("EMAILS_ENABLED", mode="before")
    @classmethod
    def get_emails_enabled(cls, v: bool, info: ValidationInfo) -> bool:
        return bool(
            info.data.get("SMTP_HOST")
            and info.data.get("SMTP_PORT")
            and info.data.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@email.com"
    PHONE_TEST_USER: str = f"{random.randint(1000000000, 9999999999)}"
    CPF_TEST_USER: str = f"{random.randint(1000000000, 9999999999)}"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False

    model_config = SettingsConfigDict(case_sensitive=True)


load_dotenv()
settings = Settings()
