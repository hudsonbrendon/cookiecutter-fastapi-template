from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    token_acesso: str
    tipo_token: str


class CargaToken(BaseModel):
    sub: Optional[int] = None
