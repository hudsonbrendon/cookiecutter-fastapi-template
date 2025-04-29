from typing import Any, Dict, Optional, Union

from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.security import obter_hash_senha, verificar_senha
from app.crud.base import CRUDBase
from app.models.user import Usuario
from app.schemas.user import AtualizarUsuario, CriarUsuario


class CRUDUsuario(CRUDBase[Usuario, CriarUsuario, AtualizarUsuario]):
    """O CRUD para o modelo de Usuário.

    Args:
        CRUDBase (_type_): O CRUD base.

    Returns:
        _type_: O CRUD para o modelo de Usuário.
    """

    @staticmethod
    def obter_por_email(db: Session, *, email: EmailStr) -> Optional[Usuario]:
        """Filtrar por e-mail.

        Args:
            db (Session): A sessão do banco de dados.
            email (EmailStr): O e-mail.

        Returns:
            Optional[Usuario]: O usuário.
        """
        return db.query(Usuario).filter(Usuario.email == email).first()

    @staticmethod
    def obter_por_cpf(db: Session, *, cpf: str) -> Optional[Usuario]:
        """Filtrar por CPF.

        Args:
            db (Session): A sessão do banco de dados.
            cpf (str): O CPF.

        Returns:
            Optional[Usuario]: O usuário.
        """
        return db.query(Usuario).filter(Usuario.cpf == cpf).first()

    def criar(self, db: Session, *, obj_in: CriarUsuario) -> Usuario:
        """Criar usuário.

        Args:
            db (Session): A sessão do banco de dados.
            obj_in (CriarUsuario): O modelo de criação de usuário.

        Returns:
            Usuario: O usuário.
        """
        db_obj = Usuario(
            primeiro_nome=obj_in.primeiro_nome,
            sobrenome=obj_in.sobrenome,
            cpf=obj_in.cpf,
            email=obj_in.email,
            telefone=obj_in.telefone,
            permissao=obj_in.permissao,
            senha_criptografada=obter_hash_senha(obj_in.senha),
            eh_superusuario=obj_in.eh_superusuario,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def atualizar(
        self,
        db: Session,
        *,
        db_obj: Usuario,
        obj_in: Union[AtualizarUsuario, Dict[str, Any]],
    ) -> Usuario:
        """Atualizar usuário.

        Args:
            db (Session): A sessão do banco de dados.
            db_obj (Usuario): O usuário.
            obj_in (Union[AtualizarUsuario, Dict[str, Any]]): O modelo de atualização de usuário.

        Returns:
            Usuario: O usuário.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if update_data["senha"]:
            senha_criptografada = obter_hash_senha(update_data["senha"])
            del update_data["senha"]
            update_data["senha_criptografada"] = senha_criptografada
        return super().atualizar(db, db_obj=db_obj, obj_in=update_data)

    def autenticar(self, db: Session, *, email: str, senha: str) -> Optional[Usuario]:
        """Autenticar usuário.

        Args:
            db (Session): A sessão do banco de dados.
            email (str): O e-mail.
            senha (str): A senha.

        Returns:
            Optional[Usuario]: O usuário.
        """
        usuario = self.obter_por_email(db, email=email)
        if not usuario:
            return None
        if not verificar_senha(senha, usuario.senha_criptografada):
            return None
        return usuario

    @staticmethod
    def esta_ativo(usuario: Usuario) -> bool:
        """Verifica se o usuário está ativo.

        Args:
            usuario (Usuario): O usuário.

        Returns:
            bool: O usuário está ativo.
        """
        return usuario.esta_ativo

    @staticmethod
    def eh_superusuario(usuario: Usuario) -> bool:
        """Verifica se o usuário é superusuário.

        Args:
            usuario (Usuario): O usuário.

        Returns:
            bool: O usuário é superusuário.
        """
        return usuario.eh_superusuario


usuario = CRUDUsuario(Usuario)
