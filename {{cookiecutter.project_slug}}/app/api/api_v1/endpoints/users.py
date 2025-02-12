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
    """List all users.

    Args:
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The number of records to return. Defaults to 100.
        _ (models.User, optional): The current user. Defaults to Depends(deps.get_current_active_superuser).

    Raises:
        HTTPException: Unable to validate credentials.

    Returns:
        Any: The list of users.
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
    """Create a new user.

    Args:
        user_in (schemas.UserCreate): The user data.
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).
        _ (models.User, optional): The current user. Defaults to Depends(deps.get_current_active_superuser).

    Raises:
        HTTPException: Unable to validate credentials.

    Returns:
        Any: The new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
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
    first_name: str = Body(None),
    last_name: str = Body(None),
    cpf: str = Body(None),
    phone: str = Body(None),
    password: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Update the current user.

    Args:
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).
        first_name (str, optional): The first name. Defaults to Body(None).
        last_name (str, optional): The last name. Defaults to Body(None).
        cpf (str, optional): The CPF. Defaults to Body(None).
        phone (str, optional): The phone number. Defaults to Body(None).
        password (str, optional): The password. Defaults to Body(None).
        email (EmailStr, optional): The email. Defaults to Body(None).
        current_user (models.User, optional): The current user. Defaults to Depends(deps.get_current_active_user).

    Raises:
        HTTPException: Unable to validate credentials.

    Returns:
        Any: The updated user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)

    if first_name is not None:
        user_in.first_name = first_name
    if last_name is not None:
        user_in.last_name = last_name
    if cpf is not None:
        user_in.cpf = cpf
    if email is not None:
        user_in.email = email
    if phone is not None:
        user_in.phone = phone
    if password is not None:
        user_in.password = password

    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get the current user.

    Args:
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).
        current_user (models.User, optional): The current user. Defaults to Depends(deps.get_current_active_user).

    Raises:
        HTTPException: Unable to validate credentials.

    Returns:
        Any: The current user.
    """
    return current_user


@router.post("/open", response_model=schemas.User)
def create_user_open(
    *,
    db: Session = Depends(deps.get_db),
    first_name: str = Body(None),
    last_name: str = Body(None),
    cpf: str = Body(...),
    email: EmailStr = Body(...),
    phone: str = Body(...),
    password: str = Body(...),
) -> Any:
    """Create a new user without the need to be logged in.

    Args:
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).
        first_name (str, optional): The full name. Defaults to Body(...).
        last_name (str, optional): The last name. Defaults to Body(...).
        cpf (str, optional): The CPF. Defaults to Body(...).
        email (EmailStr, optional): The email. Defaults to Body(...).
        phone (str, optional): The phone number. Defaults to Body(...).
        password (str, optional): The password. Defaults to Body(...).

    Raises:
        HTTPException: Open user registration is prohibited on this server.

    Returns:
        Any: The new user.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is prohibited on this server.",
        )
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_in = schemas.UserCreate(
        first_name=first_name,
        last_name=last_name,
        cpf=cpf,
        email=email,
        phone=phone,
        permission=models.UserPermissionEnum.USER.value,
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
    """Get a specific user by ID.

    Args:
        user_id (int): The user ID.
        current_user (models.User, optional): The current user. Defaults to Depends(deps.get_current_active_user).
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).

    Raises:
        HTTPException: The user does not have sufficient privileges.

    Returns:
        Any: The user.
    """
    user = crud.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400,
            detail="The user does not have sufficient privileges.",
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
    """Update a user.

    Args:
        user_id (int): The user ID.
        user_in (schemas.UserUpdate): The user data.
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).
        _ (models.User, optional): The current user. Defaults to Depends(deps.get_current_active_superuser).

    Raises:
        HTTPException: Unable to validate credentials.

    Returns:
        Any: The updated user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
