from sqlalchemy import Boolean, Column, Integer, String

from app.db.base_class import Base


class User(Base):
    """User model.

    Args:
        Base (_type_): Base class for SQLAlchemy model.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    cpf = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    permission = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    @property
    def full_name(self) -> str:
        """Get the full name of the user.

        Returns:
            str: The full name of the user.
        """
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        """Get the string representation of the user.

        Returns:
            str: The string representation of the user.
        """
        return f"<User full_name={self.full_name}, cpf={self.cpf}, email={self.email}, phone={self.phone}>"

    def __str__(self) -> str:
        """Get the string representation of the user.

        Returns:
            str: The string representation of the user.
        """
        return f"{self.full_name} - {self.cpf} - {self.email} - {self.phone}"
