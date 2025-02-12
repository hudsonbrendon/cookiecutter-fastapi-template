from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.core.enums import UserPermissionEnum
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.utils import random_cpf, random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, cpf: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "cpf": cpf, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    email = random_email()
    cpf = random_cpf()
    password = random_lower_string()
    user_in = UserCreate(
        username=email,
        email=email,
        cpf=cpf,
        permission=UserPermissionEnum.USER.value,
        password=password,
    )
    user = crud.user.create(db=db, obj_in=user_in)
    return user


def authentication_token_from_email(
    *,
    client: TestClient,
    email: str,
    phone: str,
    cpf: str,
    db: Session,
    is_active: bool = True,
) -> Dict[str, str]:
    """
    Retorne um token válido para o usuário com determinado email.

    Se o usuário não existir, ele será criado primeiro.
    """
    password = "test@123"
    user = crud.user.get_by_email(db, email=email)
    if not user:
        user_in_create = UserCreate(
            email=email,
            cpf=cpf,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
            is_active=is_active,
        )
        crud.user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        crud.user.update(db, db_obj=user, obj_in=user_in_update)

    return user_authentication_headers(
        client=client, email=email, cpf=cpf, password=password
    )
