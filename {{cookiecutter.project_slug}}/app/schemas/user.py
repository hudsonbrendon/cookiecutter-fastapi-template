from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    nome_completo: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    cpf: str
    email: EmailStr
    telefone: str
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
