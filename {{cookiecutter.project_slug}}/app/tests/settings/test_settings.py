import os
from io import StringIO
from typing import Any

from app.core.config import Configuracoes
from app.tests.utils.utils import (
    email_aleatorio,
    texto_aleatorio_minusculo,
    url_aleatoria,
)
from dotenv import load_dotenv


def make_settings(env_items: dict[str, Any]):
    os.environ.clear()
    env_file_settings = StringIO()
    for key, value in env_items.items():
        env_file_settings.write(f"{key}={value}\n")
    env_file_settings.seek(0)
    load_dotenv(stream=env_file_settings)
    return Configuracoes()


OBRIGATORIOS = {
    "MINUTOS_EXPIRACAO_TOKEN_ACESSO": 30,
    "SENHA_PRIMEIRO_SUPERUSUARIO": texto_aleatorio_minusculo(),
    "PRIMEIRO_SUPERUSUARIO": email_aleatorio(),
    "BD_POSTGRES": texto_aleatorio_minusculo(),
    "BD_POSTGRES_TESTE": texto_aleatorio_minusculo(),
    "SENHA_POSTGRES": texto_aleatorio_minusculo(),
    "SERVIDOR_POSTGRES": texto_aleatorio_minusculo(),
    "USUARIO_POSTGRES": texto_aleatorio_minusculo(),
    "NOME_PROJETO": texto_aleatorio_minusculo(),
    "SERVIDOR_HOST": url_aleatoria(),
    "HOST_REDIS": url_aleatoria(),
    "LIMITE_TAXA_TEMPO": "1000/minute",
}


def test_mandatory_and_defaults() -> None:
    settings = make_settings(OBRIGATORIOS)
    for key, value in OBRIGATORIOS.items():
        assert str(getattr(settings, key)) == str(value)
    assert settings.MINUTOS_EXPIRACAO_TOKEN_ACESSO == 30
    assert settings.DIR_MODELOS_EMAIL == "/app/app/modelos-email/build"
    assert settings.EMAILS_HABILITADOS is False
    assert settings.EMAILS_DE_EMAIL is None
    assert settings.EMAILS_DE_NOME == settings.NOME_PROJETO
    assert settings.HORAS_EXPIRACAO_TOKEN_REDEFINICAO_EMAIL == 48
    assert settings.EMAIL_USUARIO_TESTE == "teste@email.com"
    assert settings.DIR_MODELOS_EMAIL == "/app/app/modelos-email/build"
    assert settings.HOST_REDIS == OBRIGATORIOS["HOST_REDIS"]
    assert settings.LIMITE_TAXA_TEMPO == "1000/minute"


def test_assemble_db_connection() -> None:
    settings = make_settings(OBRIGATORIOS)
    assert str(settings.URI_BD_SQLALCHEMY) == (
        f"postgresql://{settings.USUARIO_POSTGRES}:"
        f"{settings.SENHA_POSTGRES}@{settings.SERVIDOR_POSTGRES}/"
        f"{settings.BD_POSTGRES}"
    )


def test_assemble_db_test_connection() -> None:
    settings = make_settings(OBRIGATORIOS)
    assert str(settings.URI_BD_SQLALCHEMY_TESTE) == (
        f"postgresql://{settings.USUARIO_POSTGRES}:"
        f"{settings.SENHA_POSTGRES}@{settings.SERVIDOR_POSTGRES}/"
        f"{settings.BD_POSTGRES_TESTE}"
    )


def test_backend_cors_origins() -> None:
    settings = make_settings(
        OBRIGATORIOS
        | {"ORIGENS_CORS_BACKEND": '["http://localhost", "http://localhost:3000"]'}
    )
    assert [str(item) for item in settings.ORIGENS_CORS_BACKEND] == [
        "http://localhost/",
        "http://localhost:3000/",
    ]


def test_email_enabled() -> None:
    settings = make_settings(
        OBRIGATORIOS
        | {
            "HOST_SMTP": "www.example.com",
            "PORTA_SMTP": 25,
            "EMAILS_DE_EMAIL": email_aleatorio(),
        }
    )
    assert settings.EMAILS_HABILITADOS is True
