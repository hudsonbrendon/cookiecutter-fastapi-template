from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.enums import UserPermissionEnum


class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    phone: Optional[str] = None
    permission: UserPermissionEnum
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    cpf: str
    email: EmailStr
    phone: str
    permission: UserPermissionEnum
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
