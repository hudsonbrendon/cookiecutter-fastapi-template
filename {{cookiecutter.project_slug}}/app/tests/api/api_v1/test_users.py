from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import configuracoes
from app.core.enums import EnumPermissaoUsuario
from app.schemas.user import CriarUsuario
from app.tests.utils.utils import (
    cpf_aleatorio,
    email_aleatorio,
    telefone_aleatorio,
    texto_aleatorio_minusculo,
)


class TestAPIUsuario:
    def test_obter_usuarios_superusuario_eu(
        self, client: TestClient, cabecalhos_token_superusuario: Dict[str, str]
    ) -> None:
        r = client.get(
            f"{configuracoes.API_V1_STR}/usuarios/eu",
            headers=cabecalhos_token_superusuario,
        )
        usuario_atual = r.json()
        assert usuario_atual
        assert usuario_atual["esta_ativo"] is True
        assert usuario_atual["eh_superusuario"]
        assert usuario_atual["email"] == configuracoes.PRIMEIRO_SUPERUSUARIO

    def test_obter_usuarios_usuario_normal_eu(
        self, client: TestClient, cabecalhos_token_usuario_normal: Dict[str, str]
    ) -> None:
        r = client.get(
            f"{configuracoes.API_V1_STR}/usuarios/eu",
            headers=cabecalhos_token_usuario_normal,
        )
        usuario_atual = r.json()
        assert usuario_atual
        assert usuario_atual["esta_ativo"] is True
        assert usuario_atual["eh_superusuario"] is False
        assert usuario_atual["email"] == configuracoes.EMAIL_USUARIO_TESTE

    def test_criar_usuario_novo_email(
        self, client: TestClient, cabecalhos_token_superusuario: dict, db: Session
    ) -> None:
        cpf = cpf_aleatorio()
        email = email_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()
        dados = {
            "cpf": cpf,
            "email": email,
            "telefone": telefone,
            "permissao": EnumPermissaoUsuario.USUARIO.value,
            "senha": senha,
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/usuarios/",
            headers=cabecalhos_token_superusuario,
            json=dados,
        )
        assert 200 <= r.status_code < 300
        usuario_criado = r.json()
        usuario = crud.usuario.obter_por_email(db, email=email)
        assert usuario
        assert usuario.email == usuario_criado["email"]

    def test_obter_usuario_existente(
        self, client: TestClient, cabecalhos_token_superusuario: dict, db: Session
    ) -> None:
        cpf = texto_aleatorio_minusculo()
        email = email_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()
        usuario_in = CriarUsuario(
            cpf=cpf,
            email=email,
            telefone=telefone,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            senha=senha,
        )
        usuario = crud.usuario.criar(db, obj_in=usuario_in)
        id_usuario = usuario.id
        r = client.get(
            f"{configuracoes.API_V1_STR}/usuarios/{id_usuario}",
            headers=cabecalhos_token_superusuario,
        )
        assert 200 <= r.status_code < 300
        api_usuario = r.json()
        usuario_existente = crud.usuario.obter_por_email(db, email=email)
        assert usuario_existente
        assert usuario_existente.email == api_usuario["email"]

    def test_criar_usuario_por_usuario_normal(
        self, client: TestClient, cabecalhos_token_usuario_normal: Dict[str, str]
    ) -> None:
        email = email_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()
        cpf = texto_aleatorio_minusculo()
        dados = {
            "cpf": cpf,
            "email": email,
            "telefone": telefone,
            "senha": senha,
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/usuarios/",
            headers=cabecalhos_token_usuario_normal,
            json=dados,
        )
        assert r.status_code == 400

    def test_recuperar_usuarios(
        self, client: TestClient, cabecalhos_token_superusuario: dict, db: Session
    ) -> None:
        cpf = cpf_aleatorio()
        email = email_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()

        usuario_in = CriarUsuario(
            email=email,
            telefone=telefone,
            cpf=cpf,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            senha=senha,
        )
        crud.usuario.criar(db, obj_in=usuario_in)

        cpf2 = cpf_aleatorio()
        email2 = email_aleatorio()
        telefone2 = telefone_aleatorio()
        senha2 = texto_aleatorio_minusculo()

        usuario_in2 = CriarUsuario(
            cpf=cpf2,
            email=email2,
            telefone=telefone2,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            senha=senha2,
        )
        crud.usuario.criar(db, obj_in=usuario_in2)

        r = client.get(
            f"{configuracoes.API_V1_STR}/usuarios/",
            headers=cabecalhos_token_superusuario,
        )
        todos_usuarios = r.json()

        assert len(todos_usuarios) > 1
        for item in todos_usuarios:
            assert "email" in item
