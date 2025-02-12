from typing import Any, Dict, Optional, Union

from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """The CRUD for User model.

    Args:
        CRUDBase (_type_): The base CRUD.

    Returns:
        _type_: The CRUD for User model.
    """

    @staticmethod
    def get_by_email(db: Session, *, email: EmailStr) -> Optional[User]:
        """Filter by email.

        Args:
            db (Session): The database session.
            email (EmailStr): The email.

        Returns:
            Optional[User]: The user.
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_cpf(db: Session, *, cpf: str) -> Optional[User]:
        """Filter by CPF.

        Args:
            db (Session): The database session.
            cpf (str): The CPF.

        Returns:
            Optional[User]: The user.
        """
        return db.query(User).filter(User.cpf == cpf).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Criar usuário.

        Args:
            db (Session): The database session.
            obj_in (UserCreate): The user creation model.

        Returns:
            User: The user.
        """
        db_obj = User(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            cpf=obj_in.cpf,
            email=obj_in.email,
            phone=obj_in.phone,
            permission=obj_in.permission,
            hashed_password=get_password_hash(obj_in.password),
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update user.

        Args:
            db (Session): The database session.
            db_obj (User): The user.
            obj_in (Union[UserUpdate, Dict[str, Any]]): The user update model.

        Returns:
            User: The user.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate user.

        Args:
            db (Session): The database session.
            email (str): The email.
            password (str): The password.

        Returns:
            Optional[User]: The user.
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def is_active(user: User) -> bool:
        """Verify if the user is active.

        Args:
            user (User): The user.

        Returns:
            bool: The user is active.
        """
        return user.is_active

    @staticmethod
    def is_superuser(user: User) -> bool:
        """Verify if the user is superuser.

        Args:
            user (User): The user.

        Returns:
            bool: The user is superuser.
        """
        return user.is_superuser


user = CRUDUser(User)
