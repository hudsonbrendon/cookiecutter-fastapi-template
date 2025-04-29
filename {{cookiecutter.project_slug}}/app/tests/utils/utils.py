import random
import secrets
import string
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import configuracoes


def texto_aleatorio_minusculo() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def data_aleatoria() -> str:
    """Data aleatória no formato AAAA-MM-DD"""
    return (
        f"{random.randint(1900, 2020)}-{random.randint(1, 12)}-{random.randint(1, 28)}"
    )


def inteiro_aleatorio() -> int:
    return random.randint(1, 9999999999)


def flutuante_aleatorio() -> float:
    return random.uniform(1, 9999999999)


def email_aleatorio() -> str:
    return f"{texto_aleatorio_minusculo()}@{texto_aleatorio_minusculo()}.com"


def cpf_aleatorio() -> str:
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


def telefone_aleatorio() -> str:
    return f"{random.randint(1000000000, 9999999999)}"


def url_aleatoria() -> str:
    return f"https://{texto_aleatorio_minusculo()}.com/"


def obter_cabecalhos_token_superusuario(client: TestClient) -> Dict[str, str]:
    dados_login = {
        "username": configuracoes.PRIMEIRO_SUPERUSUARIO,
        "password": configuracoes.SENHA_PRIMEIRO_SUPERUSUARIO,
    }
    r = client.post(f"{configuracoes.API_V1_STR}/login/token-acesso", data=dados_login)
    tokens = r.json()
    token_acesso = tokens["token_acesso"]
    cabecalhos = {"Authorization": f"Bearer {token_acesso}"}
    return cabecalhos
