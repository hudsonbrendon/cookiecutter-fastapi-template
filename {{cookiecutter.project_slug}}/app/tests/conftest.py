from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from app.schemas.user import UserCreate
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import (
    get_superuser_token_headers,
    random_cpf,
    random_email,
    random_telefone,
)


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client,
        email=settings.EMAIL_TEST_USER,
        telefone=settings.TELEFONE_TEST_USER,
        cpf=settings.CPF_TEST_USER,
        db=db,
    )


@pytest.fixture(scope="module")
def random_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client,
        email=random_email(),
        telefone=random_telefone(),
        cpf=random_cpf(),
        db=db,
    )

@pytest.fixture(scope="module")
def user_inactive_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client,
        email=random_email(),
        telefone=random_telefone(),
        cpf=random_cpf(),
        is_active=False,
        db=db,
    )


@pytest.fixture
def db_user(db: Session) -> User:
    user_in = UserCreate(
        email=random_email(),
        telefone=random_telefone(),
        cpf=random_cpf(),
        password="test@123",
    )
    return crud.user.create(db, obj_in=user_in)
