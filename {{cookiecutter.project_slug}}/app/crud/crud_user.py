from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD Usuario."""

    @staticmethod
    def get_by_email(db: Session, *, email: str) -> Optional[User]:
        """Filtre por email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_cpf(db: Session, *, cpf: str) -> Optional[User]:
        """Filtre por cpf."""
        return db.query(User).filter(User.cpf == cpf).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Criar novo usuário."""
        db_obj = User(
            nome_completo=obj_in.nome_completo,
            cpf=obj_in.cpf,
            email=obj_in.email,
            telefone=obj_in.telefone,
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
        """Atualizar usuário."""
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
        """Autenticar usuário."""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def is_active(user: User) -> bool:
        """Verifica se o usuário está ativo."""
        return user.is_active

    @staticmethod
    def is_superuser(user: User) -> bool:
        """Verifica se o usuário é superusuário."""
        return user.is_superuser


user = CRUDUser(User)
