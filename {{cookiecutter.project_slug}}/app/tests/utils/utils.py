import random
import secrets
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
    cpf = [secrets.randbelow(10) for _ in range(9)]

    # Calcula o primeiro dígito verificador
    soma = sum([(10 - i) * cpf[i] for i in range(9)])
    primeiro_digito = (soma * 10) % 11
    primeiro_digito = 0 if primeiro_digito == 10 else primeiro_digito

    # Adiciona o primeiro dígito verificador ao CPF
    cpf.append(primeiro_digito)

    # Calcula o segundo dígito verificador
    soma = sum([(11 - i) * cpf[i] for i in range(10)])
    segundo_digito = (soma * 10) % 11
    segundo_digito = 0 if segundo_digito == 10 else segundo_digito

    # Adiciona o segundo dígito verificador ao CPF
    cpf.append(segundo_digito)

    # Converte a lista de dígitos em uma string formatada
    cpf_formatado = "".join(map(str, cpf))
    return cpf_formatado


def random_phone() -> str:
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
