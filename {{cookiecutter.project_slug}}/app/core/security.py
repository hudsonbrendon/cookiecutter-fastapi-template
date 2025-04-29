from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import configuracoes

contexto_senha = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITMO = "HS256"


def criar_token_acesso(
    assunto: Union[str, Any], delta_expiracao: timedelta = None
) -> str:
    """Cria um token de acesso.

    Args:
        assunto (Union[str, Any]): O assunto.
        delta_expiracao (timedelta, optional): O tempo de expiração. Padrão é None.

    Returns:
        str: O token de acesso.
    """
    if delta_expiracao:
        expira = datetime.utcnow() + delta_expiracao
    else:
        expira = datetime.utcnow() + timedelta(
            minutes=configuracoes.MINUTOS_EXPIRACAO_TOKEN_ACESSO
        )
    para_codificar = {"exp": expira, "sub": str(assunto)}
    jwt_codificado = jwt.encode(
        para_codificar, configuracoes.CHAVE_SECRETA, algorithm=ALGORITMO
    )
    return jwt_codificado


def verificar_senha(senha_texto: str, senha_hash: str) -> bool:
    """Verifica a senha.

    Args:
        senha_texto (str): A senha em texto plano.
        senha_hash (str): A senha criptografada.

    Returns:
        bool: True se a senha for válida.
    """
    return contexto_senha.verify(senha_texto, senha_hash)


def obter_hash_senha(senha: str) -> str:
    """Obtém o hash da senha.

    Args:
        senha (str): A senha.

    Returns:
        str: O hash da senha.
    """
    return contexto_senha.hash(senha)
