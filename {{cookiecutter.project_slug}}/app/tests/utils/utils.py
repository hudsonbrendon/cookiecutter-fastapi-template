import random
import string
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_date() -> str:
    """Random date in format YYYY-MM-DD"""
    return (
        f"{random.randint(1900, 2020)}-{random.randint(1, 12)}-{random.randint(1, 28)}"
    )


def random_int() -> int:
    return random.randint(1, 9999999999)


def random_float() -> float:
    return random.uniform(1, 9999999999)


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_cpf() -> str:
    return f"{random.randint(1000000000, 9999999999)}"


def random_telefone() -> str:
    return f"{random.randint(1000000000, 9999999999)}"


def random_url() -> str:
    return f"https://{random_lower_string()}.com/"


def get_superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
