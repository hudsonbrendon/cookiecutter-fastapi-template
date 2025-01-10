from sqlalchemy import Boolean, Column, Integer, String

from app.db.base_class import Base


class User(Base):
    """Modelo de usuário."""

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String, index=True)
    cpf = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
