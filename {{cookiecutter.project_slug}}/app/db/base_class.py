from typing import Any

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    """Classe base para o modelo SQLAlchemy.

    Returns:
        _type_: A classe base para o modelo SQLAlchemy.
    """

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Obtém o nome da tabela.

        Returns:
            str: O nome da tabela.
        """
        return cls.__name__.lower()
