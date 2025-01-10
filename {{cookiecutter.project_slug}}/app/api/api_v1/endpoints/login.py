"""Endpoints relacionados a login e token."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
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
    error_message="Muitas tentativas de login. Tente novamente mais tarde.",
)
def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatível com login para acesso de token JWT.
    """
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha inválidos.")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Usuário inativo.")
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
    """
    Resetar senha.
    """
    user_id = verify_password_reset_token(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido.")

    user = crud.user.get(db, id=user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )

    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Usuário inativo.")

    elif not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual inválida.")

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    user.primeiro_acesso = False
    db.add(user)
    db.commit()
    return {"msg": "Senha alterada com sucesso."}


@router.post("/create-password/", response_model=schemas.Msg)
async def create_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Criar senha.
    """
    user_id = verify_password_reset_token(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Token inválido.")

    user = crud.user.get(db, id=user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )

    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Usuário inativo.")

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Senha criada com sucesso."}
