"""This module is responsible for initializing the database."""

from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.core.enums import UserPermissionEnum
from app.tests.utils.utils import random_cpf, random_phone


def init_db(db: Session) -> None:
    """Inicialize o banco de dados."""
    # Tabelas devem ser criadas com migrações do Alembic
    # Mas se você não quiser usar migrações, crie
    # as tabelas descomentando a próxima linha
    # Base.metadata.create_all(bind=engine)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)

    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            phone=random_phone(),
            cpf=random_cpf(),
            permission=UserPermissionEnum.ADMINISTRATOR.value,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        crud.user.create(db, obj_in=user_in)
