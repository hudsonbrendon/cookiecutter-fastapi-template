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
from app.core.config import configuracoes
from app.core.security import obter_hash_senha, verificar_senha
from app.utils import verificar_token_redefinicao_senha

limitador = Limiter(key_func=get_remote_address)


router = APIRouter()


@router.post("/login/token-acesso", response_model=schemas.Token)
@limitador.limit(
    limit_value=configuracoes.LIMITE_TAXA_TEMPO,
    error_message="Muitas tentativas de login. Por favor, tente novamente mais tarde.",
)
def login_token_acesso(
    request: Request,
    db: Session = Depends(deps.obter_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """Fazer login e obter token de acesso.

    Args:
        request (Request): A requisição.
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).
        form_data (OAuth2PasswordRequestForm, optional): Os dados do formulário. Padrão é Depends().

    Raises:
        HTTPException: Nome de usuário ou senha inválidos.

    Returns:
        Any: O token de acesso.
    """
    usuario = crud.usuario.autenticar(
        db, email=form_data.username, senha=form_data.password
    )
    if not usuario:
        raise HTTPException(
            status_code=400, detail="Nome de usuário ou senha inválidos."
        )
    elif not crud.usuario.esta_ativo(usuario):
        raise HTTPException(status_code=400, detail="Usuário inativo.")
    expiracao_token_acesso = timedelta(
        minutes=configuracoes.MINUTOS_EXPIRACAO_TOKEN_ACESSO
    )
    return {
        "token_acesso": security.criar_token_acesso(
            usuario.id, delta_expiracao=expiracao_token_acesso
        ),
        "tipo_token": "bearer",
    }


@router.post("/redefinir-senha/", response_model=schemas.Mensagem)
async def redefinir_senha(
    token: str = Body(...),
    senha_antiga: str = Body(...),
    senha_nova: str = Body(...),
    db: Session = Depends(deps.obter_db),
) -> Any:
    """Redefinir senha.

    Args:
        token (str, optional): O token. Padrão é Body(...).
        senha_antiga (str, optional): A senha antiga. Padrão é Body(...).
        senha_nova (str, optional): A senha nova. Padrão é Body(...).
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).

    Raises:
        HTTPException: Token inválido.

    Returns:
        Any: A mensagem.
    """
    id_usuario = verificar_token_redefinicao_senha(token)
    if not id_usuario:
        raise HTTPException(status_code=400, detail="Token inválido.")

    usuario = crud.usuario.obter(db, id=id_usuario)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )

    elif not crud.usuario.esta_ativo(usuario):
        raise HTTPException(status_code=400, detail="Usuário inativo.")

    elif not verificar_senha(senha_antiga, usuario.senha_criptografada):
        raise HTTPException(status_code=400, detail="A senha atual é inválida.")

    hash_senha = obter_hash_senha(senha_nova)
    usuario.senha_criptografada = hash_senha
    usuario.primeiro_acesso = False
    db.add(usuario)
    db.commit()
    return {"msg": "Senha alterada com sucesso."}


@router.post("/criar-senha/", response_model=schemas.Mensagem)
async def criar_senha(
    token: str = Body(...),
    senha_nova: str = Body(...),
    db: Session = Depends(deps.obter_db),
) -> Any:
    """Criar senha.

    Args:
        token (str, optional): O token. Padrão é Body(...).
        senha_nova (str, optional): A senha nova. Padrão é Body(...).
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).

    Raises:
        HTTPException: Token inválido.

    Returns:
        Any: A mensagem.
    """
    id_usuario = verificar_token_redefinicao_senha(token)
    if not id_usuario:
        raise HTTPException(status_code=400, detail="Token inválido.")

    usuario = crud.usuario.obter(db, id=id_usuario)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )

    elif not crud.usuario.esta_ativo(usuario):
        raise HTTPException(status_code=400, detail="Usuário inativo.")

    hash_senha = obter_hash_senha(senha_nova)
    usuario.senha_criptografada = hash_senha
    db.add(usuario)
    db.commit()
    return {"msg": "Senha criada com sucesso."}
