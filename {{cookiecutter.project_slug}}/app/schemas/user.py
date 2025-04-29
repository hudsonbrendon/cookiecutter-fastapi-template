from typing import Optional

from pydantic import BaseModel, EmailStr

from app.core.enums import EnumPermissaoUsuario


class Usuario(BaseModel):
    primeiro_nome: Optional[str] = None
    sobrenome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    permissao: EnumPermissaoUsuario
    esta_ativo: Optional[bool] = True
    eh_superusuario: bool = False


class CriarUsuario(Usuario):
    cpf: str
    email: EmailStr
    telefone: str
    permissao: EnumPermissaoUsuario
    senha: str


class AtualizarUsuario(BaseModel):
    primeiro_nome: Optional[str] = None
    sobrenome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    esta_ativo: Optional[bool] = True
    eh_superusuario: bool = False
    senha: Optional[str] = None
