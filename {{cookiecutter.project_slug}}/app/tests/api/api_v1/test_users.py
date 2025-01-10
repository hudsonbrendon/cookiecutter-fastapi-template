from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.schemas.user import UserCreate
from app.tests.utils.utils import (
    random_cpf,
    random_email,
    random_lower_string,
    random_telefone,
)


class TestUserAPI:
    def test_get_users_superuser_me(
        self, client: TestClient, superuser_token_headers: Dict[str, str]
    ) -> None:
        r = client.get(
            f"{settings.API_V1_STR}/usuarios/me",
            headers=superuser_token_headers,
        )
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert current_user["is_superuser"]
        assert current_user["email"] == settings.FIRST_SUPERUSER

    def test_get_users_normal_user_me(
        self, client: TestClient, normal_user_token_headers: Dict[str, str]
    ) -> None:
        r = client.get(
            f"{settings.API_V1_STR}/usuarios/me",
            headers=normal_user_token_headers,
        )
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert current_user["is_superuser"] is False
        assert current_user["email"] == settings.EMAIL_TEST_USER

    def test_create_user_new_email(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ) -> None:
        cpf = random_cpf()
        email = random_email()
        telefone = random_telefone()
        password = random_lower_string()
        data = {
            "cpf": cpf,
            "email": email,
            "telefone": telefone,
            "password": password,
        }
        r = client.post(
            f"{settings.API_V1_STR}/usuarios/",
            headers=superuser_token_headers,
            json=data,
        )
        assert 200 <= r.status_code < 300
        created_user = r.json()
        user = crud.user.get_by_email(db, email=email)
        assert user
        assert user.email == created_user["email"]

    def test_get_existing_user(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ) -> None:
        cpf = random_lower_string()
        email = random_email()
        telefone = random_telefone()
        password = random_lower_string()
        user_in = UserCreate(
            cpf=cpf,
            email=email,
            telefone=telefone,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        user_id = user.id
        r = client.get(
            f"{settings.API_V1_STR}/usuarios/{user_id}",
            headers=superuser_token_headers,
        )
        assert 200 <= r.status_code < 300
        api_user = r.json()
        existing_user = crud.user.get_by_email(db, email=email)
        assert existing_user
        assert existing_user.email == api_user["email"]

    def test_create_user_by_normal_user(
        self, client: TestClient, normal_user_token_headers: Dict[str, str]
    ) -> None:
        email = random_email()
        telefone = random_telefone()
        password = random_lower_string()
        cpf = random_lower_string()
        data = {
            "cpf": cpf,
            "email": email,
            "telefone": telefone,
            "password": password,
        }
        r = client.post(
            f"{settings.API_V1_STR}/usuarios/",
            headers=normal_user_token_headers,
            json=data,
        )
        assert r.status_code == 400

    def test_retrieve_users(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ) -> None:
        cpf = random_cpf()
        email = random_email()
        telefone = random_telefone()
        password = random_lower_string()

        user_in = UserCreate(email=email, telefone=telefone, cpf=cpf, password=password)
        crud.user.create(db, obj_in=user_in)

        cpf2 = random_cpf()
        email2 = random_email()
        telefone2 = random_telefone()
        password2 = random_lower_string()

        user_in2 = UserCreate(
            cpf=cpf2, email=email2, telefone=telefone2, password=password2
        )
        crud.user.create(db, obj_in=user_in2)

        r = client.get(
            f"{settings.API_V1_STR}/usuarios/", headers=superuser_token_headers
        )
        all_users = r.json()

        assert len(all_users) > 1
        for item in all_users:
            assert "email" in item
