from typing import Dict

from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models.user import User
from app.utils import verify_password_reset_token


class TestLogin:
    def test_get_access_token_wrong_password(self, client: TestClient) -> None:
        login_data = {
            "username": settings.FIRST_SUPERUSER,
            "password": "wrongpassword",
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        assert r.status_code == 400
        assert "Invalid username or password." in r.text

    def test_get_access_token(self, client: TestClient) -> None:
        login_data = {
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        assert r.status_code == 200
        assert "access_token" in tokens
        assert tokens["access_token"]

    def test_get_access_token_user_inative(
        self, db: Session, client: TestClient, db_user: User
    ) -> None:
        db_user.is_active = False
        user_in = jsonable_encoder(db_user)
        db.query(User).filter(User.id == db_user.id).update(user_in)
        db.commit()

        login_data = {
            "username": db_user.email,
            "password": "test@123",
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        assert r.status_code == 400
        assert r.json()["detail"] == "Usuário inativo."


class TestUserMe:
    def test_user_me_superuser(
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

    def test_user_me_normal_user(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
    ) -> None:
        r = client.get(
            f"{settings.API_V1_STR}/usuarios/me",
            headers=normal_user_token_headers,
        )
        current_user = r.json()
        assert current_user
        assert current_user["is_active"] is True
        assert not current_user["is_superuser"]
        assert current_user["email"] == settings.EMAIL_TEST_USER


class TestResetPassword:
    def test_reset_password_success(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
    ) -> None:
        data = {
            "token": normal_user_token_headers["Authorization"].split(" ")[1],
            "old_password": "test@123",
            "new_password": "test@123",
        }
        r = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            json=data,
        )
        assert r.status_code == 200
        assert r.json()["msg"] == "Senha alterada com sucesso."

    def test_reset_password_with_invalid_password(
        self,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
    ) -> None:
        data = {
            "token": normal_user_token_headers["Authorization"].split(" ")[1],
            "old_password": "test@test",
            "new_password": "test@123",
        }
        r = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            json=data,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "Senha atual inválida."

    def test_reset_password_with_invalid_token(
        self,
        client: TestClient,
    ) -> None:
        data = {
            "token": "invalid_token",
            "old_password": "test@123",
            "new_password": "test@123",
        }
        r = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            json=data,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "Token inválido."

    def test_reset_password_user_not_found(
        self,
        db: Session,
        client: TestClient,
        normal_user_token_headers: Dict[str, str],
    ) -> None:
        token = normal_user_token_headers["Authorization"].split(" ")[1]

        user_id = verify_password_reset_token(token)

        crud.user.remove(db, id=user_id)

        data = {
            "token": token,
            "old_password": "test@123",
            "new_password": "test@123",
        }
        r = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            json=data,
        )
        assert r.status_code == 404
        assert r.json()["detail"] == "Usuário não encontrado."


class TestCreatePassword:
    def test_create_password_success(
        self,
        client: TestClient,
        db: Session,
        random_user_token_headers: Dict[str, str],
    ) -> None:
        token = random_user_token_headers["Authorization"].split(" ")[1]
        data = {
            "token": token,
            "new_password": "test@123",
        }
        r = client.post(
            f"{settings.API_V1_STR}/create-password/",
            json=data,
        )
        assert r.status_code == 200
        assert r.json()["msg"] == "Senha criada com sucesso."

    def test_create_password_with_invalid_token(
        self,
        client: TestClient,
    ) -> None:
        data = {
            "token": "invalid_token",
            "new_password": "test@123",
        }
        r = client.post(
            f"{settings.API_V1_STR}/create-password/",
            json=data,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "Token inválido."

    def test_create_password_user_not_found(
        self,
        db: Session,
        client: TestClient,
        random_user_token_headers: Dict[str, str],
    ) -> None:
        token = random_user_token_headers["Authorization"].split(" ")[1]

        user_id = verify_password_reset_token(token)

        crud.user.remove(db, id=user_id)

        data = {
            "token": token,
            "new_password": "test@123",
        }
        r = client.post(
            f"{settings.API_V1_STR}/create-password/",
            json=data,
        )
        assert r.status_code == 404
        assert r.json()["detail"] == "Usuário não encontrado."
