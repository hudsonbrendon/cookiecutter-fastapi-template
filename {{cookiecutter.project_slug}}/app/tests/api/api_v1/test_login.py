from typing import Dict

from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import configuracoes
from app.models.user import Usuario
from app.utils import verificar_token_redefinicao_senha


class TestLogin:
    def test_obter_token_acesso_senha_incorreta(self, client: TestClient) -> None:
        dados_login = {
            "username": configuracoes.PRIMEIRO_SUPERUSUARIO,
            "password": "senhaincorreta",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/login/token-acesso", data=dados_login
        )
        assert r.status_code == 400
        assert "Nome de usuário ou senha inválidos." in r.text

    def test_obter_token_acesso(self, client: TestClient) -> None:
        dados_login = {
            "username": configuracoes.PRIMEIRO_SUPERUSUARIO,
            "password": configuracoes.SENHA_PRIMEIRO_SUPERUSUARIO,
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/login/token-acesso", data=dados_login
        )
        tokens = r.json()
        assert r.status_code == 200
        assert "token_acesso" in tokens
        assert tokens["token_acesso"]

    def test_obter_token_acesso_usuario_inativo(
        self, db: Session, client: TestClient, db_usuario: Usuario
    ) -> None:
        db_usuario.esta_ativo = False
        usuario_in = jsonable_encoder(db_usuario)
        db.query(Usuario).filter(Usuario.id == db_usuario.id).update(usuario_in)
        db.commit()

        dados_login = {
            "username": db_usuario.email,
            "password": "test@123",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/login/token-acesso", data=dados_login
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "Usuário inativo."


class TestUsuarioEu:
    def test_usuario_eu_superusuario(
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

    def test_usuario_eu_usuario_normal(
        self,
        client: TestClient,
        cabecalhos_token_usuario_normal: Dict[str, str],
    ) -> None:
        r = client.get(
            f"{configuracoes.API_V1_STR}/usuarios/eu",
            headers=cabecalhos_token_usuario_normal,
        )
        usuario_atual = r.json()
        assert usuario_atual
        assert usuario_atual["esta_ativo"] is True
        assert not usuario_atual["eh_superusuario"]
        assert usuario_atual["email"] == configuracoes.EMAIL_USUARIO_TESTE


class TestRedefinirSenha:
    def test_redefinir_senha_sucesso(
        self,
        client: TestClient,
        cabecalhos_token_usuario_normal: Dict[str, str],
    ) -> None:
        dados = {
            "token": cabecalhos_token_usuario_normal["Authorization"].split(" ")[1],
            "senha_antiga": "test@123",
            "senha_nova": "test@123",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/redefinir-senha/",
            json=dados,
        )
        assert r.status_code == 200
        assert r.json()["msg"] == "Senha alterada com sucesso."

    def test_redefinir_senha_com_senha_invalida(
        self,
        client: TestClient,
        cabecalhos_token_usuario_normal: Dict[str, str],
    ) -> None:
        dados = {
            "token": cabecalhos_token_usuario_normal["Authorization"].split(" ")[1],
            "senha_antiga": "test@test",
            "senha_nova": "test@123",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/redefinir-senha/",
            json=dados,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "A senha atual é inválida."

    def test_redefinir_senha_com_token_invalido(
        self,
        client: TestClient,
    ) -> None:
        dados = {
            "token": "token_invalido",
            "senha_antiga": "test@123",
            "senha_nova": "test@123",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/redefinir-senha/",
            json=dados,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "Token inválido."

    def test_redefinir_senha_usuario_nao_encontrado(
        self,
        db: Session,
        client: TestClient,
        cabecalhos_token_usuario_normal: Dict[str, str],
    ) -> None:
        token = cabecalhos_token_usuario_normal["Authorization"].split(" ")[1]

        id_usuario = verificar_token_redefinicao_senha(token)

        crud.usuario.remover(db, id=id_usuario)

        dados = {
            "token": token,
            "senha_antiga": "test@123",
            "senha_nova": "test@123",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/redefinir-senha/",
            json=dados,
        )
        assert r.status_code == 404
        assert r.json()["detail"] == "Usuário não encontrado."


class TestCriarSenha:
    def test_criar_senha_sucesso(
        self,
        client: TestClient,
        db: Session,
        cabecalhos_token_usuario_aleatorio: Dict[str, str],
    ) -> None:
        token = cabecalhos_token_usuario_aleatorio["Authorization"].split(" ")[1]
        dados = {
            "token": token,
            "senha_nova": "test@123",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/criar-senha/",
            json=dados,
        )
        assert r.status_code == 200
        assert r.json()["msg"] == "Senha criada com sucesso."

    def test_criar_senha_com_token_invalido(
        self,
        client: TestClient,
    ) -> None:
        dados = {
            "token": "token_invalido",
            "senha_nova": "test@123",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/criar-senha/",
            json=dados,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "Token inválido."

    def test_criar_senha_usuario_nao_encontrado(
        self,
        db: Session,
        client: TestClient,
        cabecalhos_token_usuario_aleatorio: Dict[str, str],
    ) -> None:
        token = cabecalhos_token_usuario_aleatorio["Authorization"].split(" ")[1]

        id_usuario = verificar_token_redefinicao_senha(token)

        crud.usuario.remover(db, id=id_usuario)

        dados = {
            "token": token,
            "senha_nova": "test@123",
        }
        r = client.post(
            f"{configuracoes.API_V1_STR}/criar-senha/",
            json=dados,
        )
        assert r.status_code == 404
        assert r.json()["detail"] == "Usuário não encontrado."
