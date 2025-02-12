from typing import Any

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    """Base class for SQLAlchemy model.

    Returns:
        _type_: The base class for SQLAlchemy model.
    """

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Get the table name.

        Returns:
            str: The table name.
        """
        return cls.__name__.lower()
