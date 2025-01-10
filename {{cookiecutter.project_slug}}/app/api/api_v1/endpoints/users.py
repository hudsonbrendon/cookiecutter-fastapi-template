"""User endpoints."""

from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import send_new_account_email

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    _: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="O usuário com este nome de usuário já existe no sistema.",
        )
    user = crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
        )
    return user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    nome_completo: str = Body(None),
    cpf: str = Body(None),
    telefone: str = Body(None),
    password: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Atualize o próprio usuário.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)

    if nome_completo is not None:
        user_in.nome_completo = nome_completo
    if cpf is not None:
        user_in.cpf = cpf
    if email is not None:
        user_in.email = email
    if telefone is not None:
        user_in.telefone = telefone
    if password is not None:
        user_in.password = password

    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtenha o usuário atual.
    """
    return current_user


@router.post("/open", response_model=schemas.User)
def create_user_open(
    *,
    db: Session = Depends(deps.get_db),
    nome_completo: str = Body(None),
    cpf: str = Body(...),
    email: EmailStr = Body(...),
    telefone: str = Body(...),
    password: str = Body(...),
) -> Any:
    """
    Crie um novo usuário sem a necessidade de estar logado.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="O registro aberto de usuário é proibido neste servidor.",
        )
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="O usuário com este nome de usuário já existe no sistema.",
        )
    user_in = schemas.UserCreate(
        nome_completo=nome_completo,
        cpf=cpf,
        email=email,
        telefone=telefone,
        password=password,
    )
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Obtenha um usuário específico por ID.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400,
            detail="O usuário não tem privilégios suficientes.",
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    _: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="O usuário com este nome de usuário não existe no sistema.",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
