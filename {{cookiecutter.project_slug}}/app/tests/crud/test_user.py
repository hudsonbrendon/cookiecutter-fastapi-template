from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.core.enums import EnumPermissaoUsuario
from app.core.security import verificar_senha
from app.schemas.user import AtualizarUsuario, CriarUsuario
from app.tests.utils.utils import (
    cpf_aleatorio,
    email_aleatorio,
    telefone_aleatorio,
    texto_aleatorio_minusculo,
)


class TestCrudUsuario:
    def test_obter_por_email(self, db: Session) -> None:
        email = email_aleatorio()
        cpf = cpf_aleatorio()
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
        usuario_2 = crud.usuario.obter_por_email(db, email=email)
        assert usuario_2
        assert usuario.email == usuario_2.email
        assert jsonable_encoder(usuario) == jsonable_encoder(usuario_2)

    def test_obter_por_email_nao_encontrado(self, db: Session) -> None:
        usuario = crud.usuario.obter_por_email(db, email="nao_encontrado@email.com")
        assert usuario is None

    def test_obter_por_cpf(self, db: Session) -> None:
        cpf = cpf_aleatorio()
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
        usuario_2 = crud.usuario.obter_por_cpf(db, cpf=cpf)
        assert usuario_2
        assert usuario.cpf == usuario_2.cpf
        assert jsonable_encoder(usuario) == jsonable_encoder(usuario_2)

    def test_obter_por_cpf_nao_encontrado(self, db: Session) -> None:
        usuario = crud.usuario.obter_por_cpf(db, cpf="00459324250")
        assert usuario is None

    def test_criar_usuario(self, db: Session) -> None:
        email = email_aleatorio()
        cpf = cpf_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()
        usuario_in = CriarUsuario(
            email=email,
            cpf=cpf,
            telefone=telefone,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            senha=senha,
        )
        usuario = crud.usuario.criar(db, obj_in=usuario_in)
        assert usuario.email == email
        assert hasattr(usuario, "senha_criptografada")

    def test_autenticar_usuario(self, db: Session) -> None:
        cpf = cpf_aleatorio()
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
        usuario_autenticado = crud.usuario.autenticar(db, email=email, senha=senha)
        assert usuario_autenticado
        assert usuario.email == usuario_autenticado.email

    def test_nao_autenticar_usuario(self, db: Session) -> None:
        email = email_aleatorio()
        senha = texto_aleatorio_minusculo()
        usuario = crud.usuario.autenticar(db, email=email, senha=senha)
        assert usuario is None

    def test_verificar_se_usuario_esta_ativo(self, db: Session) -> None:
        cpf = cpf_aleatorio()
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
        esta_ativo = crud.usuario.esta_ativo(usuario)
        assert esta_ativo is True

    def test_verificar_se_usuario_esta_ativo_inativo(self, db: Session) -> None:
        cpf = cpf_aleatorio()
        email = email_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()
        usuario_in = CriarUsuario(
            email=email,
            cpf=cpf,
            telefone=telefone,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            senha=senha,
            desativado=True,
        )
        usuario = crud.usuario.criar(db, obj_in=usuario_in)
        esta_ativo = crud.usuario.esta_ativo(usuario)
        assert esta_ativo

    def test_verificar_se_usuario_eh_superusuario(self, db: Session) -> None:
        cpf = cpf_aleatorio()
        email = email_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()
        usuario_in = CriarUsuario(
            cpf=cpf,
            email=email,
            telefone=telefone,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            senha=senha,
            eh_superusuario=True,
        )
        usuario = crud.usuario.criar(db, obj_in=usuario_in)
        eh_superusuario = crud.usuario.eh_superusuario(usuario)
        assert eh_superusuario is True

    def test_verificar_se_usuario_eh_superusuario_usuario_normal(
        self, db: Session
    ) -> None:
        cpf = cpf_aleatorio()
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
        eh_superusuario = crud.usuario.eh_superusuario(usuario)
        assert eh_superusuario is False

    def test_obter_usuario(self, db: Session) -> None:
        cpf = cpf_aleatorio()
        email = email_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()

        usuario_in = CriarUsuario(
            cpf=cpf,
            email=email,
            telefone=telefone,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            senha=senha,
            eh_superusuario=True,
        )
        usuario = crud.usuario.criar(db, obj_in=usuario_in)
        usuario_2 = crud.usuario.obter(db, id=usuario.id)
        assert usuario_2
        assert usuario.cpf == usuario_2.cpf
        assert usuario.email == usuario_2.email
        assert usuario.telefone == usuario_2.telefone
        assert usuario.eh_superusuario == usuario_2.eh_superusuario
        assert jsonable_encoder(usuario) == jsonable_encoder(usuario_2)

    def test_atualizar_usuario(self, db: Session) -> None:
        cpf = cpf_aleatorio()
        email = email_aleatorio()
        telefone = telefone_aleatorio()
        senha = texto_aleatorio_minusculo()

        usuario_in = CriarUsuario(
            email=email,
            cpf=cpf,
            telefone=telefone,
            permissao=EnumPermissaoUsuario.USUARIO.value,
            eh_superusuario=True,
            senha=senha,
        )
        usuario = crud.usuario.criar(db, obj_in=usuario_in)
        nova_senha = texto_aleatorio_minusculo()
        usuario_in_update = AtualizarUsuario(senha=nova_senha, eh_superusuario=True)
        crud.usuario.atualizar(db, db_obj=usuario, obj_in=usuario_in_update)
        usuario_2 = crud.usuario.obter(db, id=usuario.id)
        assert usuario_2
        assert usuario.cpf == usuario_2.cpf
        assert usuario.email == usuario_2.email
        assert usuario.telefone == usuario_2.telefone
        assert usuario_2.eh_superusuario is True
        assert verificar_senha(nova_senha, usuario_2.senha_criptografada)
