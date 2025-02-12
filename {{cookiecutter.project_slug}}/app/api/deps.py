from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    """Get the database session.

    Raises:
        HTTPException: Unable to validate credentials.

    Returns:
        _type_: The database session.

    Yields:
        Generator: The database session.
    """
    db: Session = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    """Get the current user.

    Args:
        db (Session, optional): The database session. Defaults to Depends(get_db).
        token (str, optional): The token. Defaults to Depends(reusable_oauth2).

    Raises:
        HTTPException: Unable to validate credentials.

    Returns:
        models.User: The current user.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unable to validate credentials.",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Get the current active user.

    Args:
        current_user (models.User, optional): The user authenticated. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: The user is not active.

    Returns:
        models.User: The current active user.
    """
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user.")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """Get the current superuser.

    Args:
        current_user (models.User, optional): The user authenticated. Defaults to Depends(get_current_active_user).

    Raises:
        HTTPException: The user does not have sufficient privileges.

    Returns:
        models.User: The current superuser.
    """
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400,
            detail="The user does not have sufficient privileges.",
        )
    return current_user
