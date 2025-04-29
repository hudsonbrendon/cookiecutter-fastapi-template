from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import configuracoes
from app.db.session import SessaoLocal

oauth2_reutilizavel = OAuth2PasswordBearer(
    tokenUrl=f"{configuracoes.API_V1_STR}/login/token-acesso"
)


def obter_db() -> Generator:
    """Obtém a sessão do banco de dados.

    Raises:
        HTTPException: Não foi possível validar as credenciais.

    Returns:
        _type_: A sessão do banco de dados.

    Yields:
        Generator: A sessão do banco de dados.
    """
    db: Session = None
    try:
        db = SessaoLocal()
        yield db
    finally:
        if db:
            db.close()


def obter_usuario_atual(
    db: Session = Depends(obter_db), token: str = Depends(oauth2_reutilizavel)
) -> models.Usuario:
    """Obtém o usuário atual.

    Args:
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(obter_db).
        token (str, optional): O token. Padrão é Depends(oauth2_reutilizavel).

    Raises:
        HTTPException: Não foi possível validar as credenciais.

    Returns:
        models.Usuario: O usuário atual.
    """
    try:
        payload = jwt.decode(
            token, configuracoes.CHAVE_SECRETA, algorithms=[security.ALGORITMO]
        )
        dados_token = schemas.CargaToken(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não foi possível validar as credenciais.",
        )
    usuario = crud.usuario.obter(db, id=dados_token.sub)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return usuario


def obter_usuario_ativo_atual(
    usuario_atual: models.Usuario = Depends(obter_usuario_atual),
) -> models.Usuario:
    """Obtém o usuário ativo atual.

    Args:
        usuario_atual (models.Usuario, optional): O usuário autenticado. Padrão é Depends(obter_usuario_atual).

    Raises:
        HTTPException: O usuário não está ativo.

    Returns:
        models.Usuario: O usuário ativo atual.
    """
    if not crud.usuario.esta_ativo(usuario_atual):
        raise HTTPException(status_code=400, detail="Usuário inativo.")
    return usuario_atual


def obter_superusuario_atual(
    usuario_atual: models.Usuario = Depends(obter_usuario_ativo_atual),
) -> models.Usuario:
    """Obtém o superusuário atual.

    Args:
        usuario_atual (models.Usuario, optional): O usuário autenticado. Padrão é Depends(obter_usuario_ativo_atual).

    Raises:
        HTTPException: O usuário não tem privilégios suficientes.

    Returns:
        models.Usuario: O superusuário atual.
    """
    if not crud.usuario.eh_superusuario(usuario_atual):
        raise HTTPException(
            status_code=400,
            detail="O usuário não tem privilégios suficientes.",
        )
    return usuario_atual
