from typing import Optional

from pydantic import BaseModel, EmailStr

from app.core.enums import UserPermissionEnum


class User(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    permission: UserPermissionEnum
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(User):
    cpf: str
    email: EmailStr
    phone: str
    permission: UserPermissionEnum
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    password: Optional[str] = None
