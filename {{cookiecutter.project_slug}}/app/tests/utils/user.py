from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import configuracoes
from app.core.enums import EnumPermissaoUsuario
from app.models.user import Usuario
from app.schemas.user import AtualizarUsuario, CriarUsuario
from app.tests.utils.utils import (
    cpf_aleatorio,
    email_aleatorio,
    texto_aleatorio_minusculo,
)


def cabecalhos_autenticacao_usuario(
    *, client: TestClient, email: str, cpf: str, senha: str
) -> Dict[str, str]:
    dados = {"username": email, "cpf": cpf, "password": senha}
    r = client.post(f"{configuracoes.API_V1_STR}/login/token-acesso", data=dados)
    resposta = r.json()
    token_auth = resposta["token_acesso"]
    cabecalhos = {"Authorization": f"Bearer {token_auth}"}
    return cabecalhos


def criar_usuario_aleatorio(db: Session) -> Usuario:
    email = email_aleatorio()
    cpf = cpf_aleatorio()
    senha = texto_aleatorio_minusculo()
    usuario_in = CriarUsuario(
        username=email,
        email=email,
        cpf=cpf,
        permissao=EnumPermissaoUsuario.USUARIO.value,
        senha=senha,
    )
    usuario = crud.usuario.criar(db=db, obj_in=usuario_in)
    return usuario


def token_autenticacao_do_email(
    *,
    client: TestClient,
    email: str,
    telefone: str,
    cpf: str,
    db: Session,
    esta_ativo: bool = True,
) -> Dict[str, str]:
    """
    Retorna um token válido para o usuário com determinado email.

    Se o usuário não existir, ele será criado primeiro.
    """
    senha = "test@123"
    usuario = crud.usuario.obter_por_email(db, email=email)
    if not usuario:
        usuario_in_criacao = CriarUsuario(
            email=email,
            cpf=cpf,
            telefone=telefone,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            senha=senha,
            esta_ativo=esta_ativo,
        )
        crud.usuario.criar(db, obj_in=usuario_in_criacao)
    else:
        usuario_in_atualizacao = AtualizarUsuario(senha=senha)
        crud.usuario.atualizar(db, db_obj=usuario, obj_in=usuario_in_atualizacao)

    return cabecalhos_autenticacao_usuario(
        client=client, email=email, cpf=cpf, senha=senha
    )
