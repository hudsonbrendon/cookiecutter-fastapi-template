from sqlalchemy import Boolean, Column, Integer, String

from app.db.base_class import Base


class Usuario(Base):
    """Modelo de Usuário.

    Args:
        Base (_type_): Classe base para o modelo SQLAlchemy.
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    primeiro_nome = Column(String, index=True)
    sobrenome = Column(String, index=True)
    cpf = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, unique=True, index=True, nullable=False)
    permissao = Column(String, nullable=False)
    senha_criptografada = Column(String, nullable=False)
    esta_ativo = Column(Boolean(), default=True)
    eh_superusuario = Column(Boolean(), default=False)

    @property
    def nome_completo(self) -> str:
        """Obtém o nome completo do usuário.

        Returns:
            str: O nome completo do usuário.
        """
        return f"{self.primeiro_nome} {self.sobrenome}"

    def __repr__(self) -> str:
        """Obtém a representação em string do usuário.

        Returns:
            str: A representação em string do usuário.
        """
        return f"<Usuario nome_completo={self.nome_completo}, cpf={self.cpf}, email={self.email}, telefone={self.telefone}>"

    def __str__(self) -> str:
        """Obtém a representação em string do usuário.

        Returns:
            str: A representação em string do usuário.
        """
        return f"{self.nome_completo} - {self.cpf} - {self.email} - {self.telefone}"
