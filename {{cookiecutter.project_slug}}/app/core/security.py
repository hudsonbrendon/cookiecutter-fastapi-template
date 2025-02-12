from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create an access token.

    Args:
        subject (Union[str, Any]): The subject.
        expires_delta (timedelta, optional): The expiration time. Defaults to None.

    Returns:
        str: The access token.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the password.

    Args:
        plain_password (str): The plain password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password is valid.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Get the password hash.

    Args:
        password (str): The password.

    Returns:
        str: The password hash.
    """
    return pwd_context.hash(password)
