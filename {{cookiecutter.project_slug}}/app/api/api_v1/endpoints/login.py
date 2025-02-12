from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.utils import verify_password_reset_token

limiter = Limiter(key_func=get_remote_address)


router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
@limiter.limit(
    limit_value=settings.RATE_LIMIT_TIME,
    error_message="Too many login attempts. Please try again later.",
)
def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """Log in and get access token.

    Args:
        request (Request): The request.
        db (Session, optional): The session database. Defaults to Depends(deps.get_db).
        form_data (OAuth2PasswordRequestForm, optional): The form data. Defaults to Depends().

    Raises:
        HTTPException: Invalid username or password.

    Returns:
        Any: The access token.
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password.")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user.")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/reset-password/", response_model=schemas.Msg)
async def reset_password(
    token: str = Body(...),
    old_password: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Reset password.

    Args:
        token (str, optional): The token. Defaults to Body(...).
        old_password (str, optional): The old password. Defaults to Body(...).
        new_password (str, optional): The new password. Defaults to Body(...).
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).

    Raises:
        HTTPException: Invalid token.

    Returns:
        Any: The message.
    """
    user_id = verify_password_reset_token(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token.")

    user = crud.user.get(db, id=user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user.")

    elif not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is invalid.")

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    user.primeiro_acesso = False
    db.add(user)
    db.commit()
    return {"msg": "Password changed successfully."}


@router.post("/create-password/", response_model=schemas.Msg)
async def create_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """Create password.

    Args:
        token (str, optional): _description_. Defaults to Body(...).
        new_password (str, optional): _description_. Defaults to Body(...).
        db (Session, optional): The database session. Defaults to Depends(deps.get_db).

    Raises:
        HTTPException: Invalid token.

    Returns:
        Any: The message.
    """
    user_id = verify_password_reset_token(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token.")

    user = crud.user.get(db, id=user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user.")

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password created successfully."}
