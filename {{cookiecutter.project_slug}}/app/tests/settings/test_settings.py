import os
from io import StringIO
from typing import Any

from dotenv import load_dotenv

from app.core.config import Settings
from app.tests.utils.utils import (
    random_email,
    random_lower_string,
    random_url,
)


def make_settings(env_items: dict[str, Any]):
    os.environ.clear()
    env_file_settings = StringIO()
    for key, value in env_items.items():
        env_file_settings.write(f"{key}={value}\n")
    env_file_settings.seek(0)
    load_dotenv(stream=env_file_settings)
    return Settings()


MANDATORY = {
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "FIRST_SUPERUSER_PASSWORD": random_lower_string(),
    "FIRST_SUPERUSER": random_email(),
    "POSTGRES_DB": random_lower_string(),
    "POSTGRES_DB_TEST": random_lower_string(),
    "POSTGRES_PASSWORD": random_lower_string(),
    "POSTGRES_SERVER": random_lower_string(),
    "POSTGRES_USER": random_lower_string(),
    "PROJECT_NAME": random_lower_string(),
    "SERVER_HOST": random_url(),
    "REDIS_HOST": random_url(),
    "RATE_LIMIT_TIME": "1000/minute",
}


def test_mandatory_and_defaults() -> None:
    settings = make_settings(MANDATORY)
    for key, value in MANDATORY.items():
        assert str(getattr(settings, key)) == str(value)
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.EMAIL_TEMPLATES_DIR == "/app/app/email-templates/build"
    assert settings.EMAILS_ENABLED is False
    assert settings.EMAILS_FROM_EMAIL is None
    assert settings.EMAILS_FROM_NAME == settings.PROJECT_NAME
    assert settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS == 48
    assert settings.EMAIL_TEST_USER == "test@email.com"
    assert settings.EMAIL_TEMPLATES_DIR == "/app/app/email-templates/build"
    assert settings.REDIS_HOST == MANDATORY["REDIS_HOST"]
    assert settings.RATE_LIMIT_TIME == "1000/minute"


def test_assemble_db_connection() -> None:
    settings = make_settings(MANDATORY)
    assert str(settings.SQLALCHEMY_DATABASE_URI) == (
        f"postgresql://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/"
        f"{settings.POSTGRES_DB}"
    )


def test_assemble_db_test_connection() -> None:
    settings = make_settings(MANDATORY)
    assert str(settings.SQLALCHEMY_DATABASE_URI_TEST) == (
        f"postgresql://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}/"
        f"{settings.POSTGRES_DB_TEST}"
    )


def test_backend_cors_origins() -> None:
    settings = make_settings(
        MANDATORY
        | {"BACKEND_CORS_ORIGINS": '["http://localhost", "http://localhost:3000"]'}
    )
    assert [str(item) for item in settings.BACKEND_CORS_ORIGINS] == [
        "http://localhost/",
        "http://localhost:3000/",
    ]


def test_email_enabled() -> None:
    settings = make_settings(
        MANDATORY
        | {
            "SMTP_HOST": "www.example.com",
            "SMTP_PORT": 25,
            "EMAILS_FROM_EMAIL": random_email(),
        }
    )
    assert settings.EMAILS_ENABLED is True
