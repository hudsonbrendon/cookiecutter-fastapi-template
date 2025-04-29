from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import configuracoes
from app.core.enums import EnumPermissaoUsuario
from app.db.session import SessaoLocal
from app.main import app
from app.models.user import Usuario
from app.schemas.user import CriarUsuario
from app.tests.utils.user import token_autenticacao_do_email
from app.tests.utils.utils import (
    cpf_aleatorio,
    email_aleatorio,
    obter_cabecalhos_token_superusuario,
    telefone_aleatorio,
)


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessaoLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def cabecalhos_token_superusuario(client: TestClient) -> Dict[str, str]:
    return obter_cabecalhos_token_superusuario(client)


@pytest.fixture(scope="module")
def cabecalhos_token_usuario_normal(client: TestClient, db: Session) -> Dict[str, str]:
    return token_autenticacao_do_email(
        client=client,
        email=configuracoes.EMAIL_USUARIO_TESTE,
        telefone=configuracoes.TELEFONE_USUARIO_TESTE,
        cpf=configuracoes.CPF_USUARIO_TESTE,
        db=db,
    )


@pytest.fixture(scope="module")
def cabecalhos_token_usuario_aleatorio(
    client: TestClient, db: Session
) -> Dict[str, str]:
    return token_autenticacao_do_email(
        client=client,
        email=email_aleatorio(),
        telefone=telefone_aleatorio(),
        cpf=cpf_aleatorio(),
        db=db,
    )


@pytest.fixture(scope="module")
def cabecalhos_token_usuario_inativo(client: TestClient, db: Session) -> Dict[str, str]:
    return token_autenticacao_do_email(
        client=client,
        email=email_aleatorio(),
        telefone=telefone_aleatorio(),
        cpf=cpf_aleatorio(),
        esta_ativo=False,
        db=db,
    )


@pytest.fixture
def db_usuario(db: Session) -> Usuario:
    usuario_in = CriarUsuario(
        email=email_aleatorio(),
        telefone=telefone_aleatorio(),
        cpf=cpf_aleatorio(),
        permissao=EnumPermissaoUsuario.USUARIO.value,
        senha="test@123",
    )
    return crud.usuario.criar(db, obj_in=usuario_in)
