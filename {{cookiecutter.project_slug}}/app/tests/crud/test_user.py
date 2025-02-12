from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud
from app.core.enums import UserPermissionEnum
from app.core.security import verify_password
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils.utils import (
    random_cpf,
    random_email,
    random_lower_string,
    random_phone,
)


class TestCrudUser:
    def test_get_by_email(self, db: Session) -> None:
        email = random_email()
        cpf = random_cpf()
        phone = random_phone()
        password = random_lower_string()
        user_in = UserCreate(
            cpf=cpf,
            email=email,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        user_2 = crud.user.get_by_email(db, email=email)
        assert user_2
        assert user.email == user_2.email
        assert jsonable_encoder(user) == jsonable_encoder(user_2)

    def test_get_by_email_not_found(self, db: Session) -> None:
        user = crud.user.get_by_email(db, email="not_found@email.com")
        assert user is None

    def test_get_by_cpf(self, db: Session) -> None:
        cpf = random_cpf()
        email = random_email()
        phone = random_phone()
        password = random_lower_string()
        user_in = UserCreate(
            cpf=cpf,
            email=email,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        user_2 = crud.user.get_by_cpf(db, cpf=cpf)
        assert user_2
        assert user.cpf == user_2.cpf
        assert jsonable_encoder(user) == jsonable_encoder(user_2)

    def test_get_by_cpf_not_found(self, db: Session) -> None:
        user = crud.user.get_by_cpf(db, cpf="00459324250")
        assert user is None

    def test_create_user(self, db: Session) -> None:
        email = random_email()
        cpf = random_cpf()
        phone = random_phone()
        password = random_lower_string()
        user_in = UserCreate(
            email=email,
            cpf=cpf,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        assert user.email == email
        assert hasattr(user, "hashed_password")

    def test_authenticate_user(self, db: Session) -> None:
        cpf = random_cpf()
        email = random_email()
        phone = random_phone()
        password = random_lower_string()
        user_in = UserCreate(
            cpf=cpf,
            email=email,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        authenticated_user = crud.user.authenticate(db, email=email, password=password)
        assert authenticated_user
        assert user.email == authenticated_user.email

    def test_not_authenticate_user(self, db: Session) -> None:
        email = random_email()
        password = random_lower_string()
        user = crud.user.authenticate(db, email=email, password=password)
        assert user is None

    def test_check_if_user_is_active(self, db: Session) -> None:
        cpf = random_cpf()
        email = random_email()
        phone = random_phone()
        password = random_lower_string()
        user_in = UserCreate(
            cpf=cpf,
            email=email,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        is_active = crud.user.is_active(user)
        assert is_active is True

    def test_check_if_user_is_active_inactive(self, db: Session) -> None:
        cpf = random_cpf()
        email = random_email()
        phone = random_phone()
        password = random_lower_string()
        user_in = UserCreate(
            email=email,
            cpf=cpf,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
            disabled=True,
        )
        user = crud.user.create(db, obj_in=user_in)
        is_active = crud.user.is_active(user)
        assert is_active

    def test_check_if_user_is_superuser(self, db: Session) -> None:
        cpf = random_cpf()
        email = random_email()
        phone = random_phone()
        password = random_lower_string()
        user_in = UserCreate(
            cpf=cpf,
            email=email,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)
        is_superuser = crud.user.is_superuser(user)
        assert is_superuser is True

    def test_check_if_user_is_superuser_normal_user(self, db: Session) -> None:
        cpf = random_cpf()
        email = random_email()
        phone = random_phone()
        password = random_lower_string()
        user_in = UserCreate(
            cpf=cpf,
            email=email,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        is_superuser = crud.user.is_superuser(user)
        assert is_superuser is False

    def test_get_user(self, db: Session) -> None:
        cpf = random_cpf()
        email = random_email()
        phone = random_phone()
        password = random_lower_string()

        user_in = UserCreate(
            cpf=cpf,
            email=email,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            password=password,
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)
        user_2 = crud.user.get(db, id=user.id)
        assert user_2
        assert user.cpf == user_2.cpf
        assert user.email == user_2.email
        assert user.phone == user_2.phone
        assert user.is_superuser == user_2.is_superuser
        assert jsonable_encoder(user) == jsonable_encoder(user_2)

    def test_update_user(self, db: Session) -> None:
        cpf = random_cpf()
        email = random_email()
        phone = random_phone()
        password = random_lower_string()

        user_in = UserCreate(
            email=email,
            cpf=cpf,
            phone=phone,
            permission=UserPermissionEnum.USER.value,
            is_superuser=True,
            password=password,
        )
        user = crud.user.create(db, obj_in=user_in)
        new_password = random_lower_string()
        user_in_update = UserUpdate(password=new_password, is_superuser=True)
        crud.user.update(db, db_obj=user, obj_in=user_in_update)
        user_2 = crud.user.get(db, id=user.id)
        assert user_2
        assert user.cpf == user_2.cpf
        assert user.email == user_2.email
        assert user.phone == user_2.phone
        assert user_2.is_superuser is True
        assert verify_password(new_password, user_2.hashed_password)
