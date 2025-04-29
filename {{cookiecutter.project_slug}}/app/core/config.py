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


def esta_executando_em_docker() -> bool:
    """Verifica se a aplicação está sendo executada em um container Docker.

    Raises:
        ValueError: Não foi possível verificar se a aplicação está sendo executada em um container Docker.

    Returns:
        bool: True se a aplicação está sendo executada em um container Docker.
    """
    if os.environ.get("AMBIENTE_SERVIDOR", "producao") == "producao":
        return True
    return os.path.exists("/.dockerenv")


class Configuracoes(BaseSettings):
    API_V1_STR: str = "/api/v1"
    CHAVE_SECRETA: str = secrets.token_urlsafe(32)
    MINUTOS_EXPIRACAO_TOKEN_ACESSO: int = 100000
    SERVIDOR_HOST: AnyHttpUrl
    # ORIGENS_CORS_BACKEND é uma lista formatada em JSON de origens
    # ex: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    ORIGENS_CORS_BACKEND: List[AnyHttpUrl] = []

    @field_validator("ORIGENS_CORS_BACKEND", mode="before")
    @classmethod
    def montar_origens_cors(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    NOME_PROJETO: str

    SERVIDOR_POSTGRES: str
    USUARIO_POSTGRES: str
    SENHA_POSTGRES: str
    BD_POSTGRES: str
    BD_POSTGRES_TESTE: Optional[str] = None
    URI_BD_SQLALCHEMY: Optional[PostgresDsn] = None
    URI_BD_SQLALCHEMY_TESTE: Optional[PostgresDsn] = None
    HOST_REDIS: str
    LIMITE_TAXA_TEMPO: Optional[str] = "1000/minute"

    @field_validator("URI_BD_SQLALCHEMY", mode="before")
    @classmethod
    def montar_conexao_bd(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        usuario = info.data.get("USUARIO_POSTGRES")
        senha = info.data.get("SENHA_POSTGRES")
        if esta_executando_em_docker():
            host = info.data.get("SERVIDOR_POSTGRES")
        else:
            host = "localhost"
        bd = info.data.get("BD_POSTGRES")

        if all([usuario, senha, host, bd]):
            return f"postgresql://{usuario}:{senha}@{host}/{bd}"
        else:
            return None

    @field_validator("URI_BD_SQLALCHEMY_TESTE", mode="before")
    @classmethod
    def montar_conexao_bd_teste(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        usuario = info.data.get("USUARIO_POSTGRES")
        senha = info.data.get("SENHA_POSTGRES")

        if esta_executando_em_docker():
            host = info.data.get("SERVIDOR_POSTGRES")
        else:
            host = "localhost"
        bd = info.data.get("BD_POSTGRES_TESTE")
        if all([usuario, senha, host, bd]):
            return f"postgresql://{usuario}:{senha}@{host}/{bd}"
        else:
            return None

    SMTP_TLS: bool = True
    PORTA_SMTP: Optional[int] = None
    HOST_SMTP: Optional[str] = None
    USUARIO_SMTP: Optional[str] = None
    SENHA_SMTP: Optional[str] = None
    EMAILS_DE_EMAIL: Optional[EmailStr] = None
    EMAILS_DE_NOME: Optional[str] = None

    @field_validator("EMAILS_DE_NOME", mode="before")
    @classmethod
    def obter_nome_projeto(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v:
            return info.data.get("NOME_PROJETO")
        return v

    HORAS_EXPIRACAO_TOKEN_REDEFINICAO_EMAIL: int = 48
    DIR_MODELOS_EMAIL: str = "/app/app/modelos-email/build"
    EMAILS_HABILITADOS: bool = False

    @field_validator("EMAILS_HABILITADOS", mode="before")
    @classmethod
    def obter_emails_habilitados(cls, v: bool, info: ValidationInfo) -> bool:
        return bool(
            info.data.get("HOST_SMTP")
            and info.data.get("PORTA_SMTP")
            and info.data.get("EMAILS_DE_EMAIL")
        )

    EMAIL_USUARIO_TESTE: EmailStr = "teste@email.com"
    TELEFONE_USUARIO_TESTE: str = f"{random.randint(1000000000, 9999999999)}"
    CPF_USUARIO_TESTE: str = f"{random.randint(1000000000, 9999999999)}"
    PRIMEIRO_SUPERUSUARIO: EmailStr
    SENHA_PRIMEIRO_SUPERUSUARIO: str
    REGISTRO_USUARIOS_ABERTO: bool = False

    model_config = SettingsConfigDict(case_sensitive=True)


load_dotenv()
configuracoes = Configuracoes()
