import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import emails
from emails.template import JinjaTemplate
from jose import jwt

from app.core.config import configuracoes


def enviar_email(
    email_para: str,
    modelo_assunto: str = "",
    modelo_html: str = "",
    environment=None,
) -> None:
    if environment is None:
        environment = {}
    assert configuracoes.EMAILS_HABILITADOS, (
        "Nenhuma configuração fornecida para variáveis de e-mail."
    )
    mensagem = emails.Message(
        subject=JinjaTemplate(modelo_assunto),
        html=JinjaTemplate(modelo_html),
        mail_from=(configuracoes.EMAILS_DE_NOME, configuracoes.EMAILS_DE_EMAIL),
    )
    opcoes_smtp = {"host": configuracoes.HOST_SMTP, "port": configuracoes.PORTA_SMTP}
    if configuracoes.SMTP_TLS:
        opcoes_smtp["tls"] = True
    if configuracoes.USUARIO_SMTP:
        opcoes_smtp["user"] = configuracoes.USUARIO_SMTP
    if configuracoes.SENHA_SMTP:
        opcoes_smtp["password"] = configuracoes.SENHA_SMTP
    resposta = mensagem.send(to=email_para, render=environment, smtp=opcoes_smtp)
    logging.info(f"resultado do envio de email: {resposta}")


def enviar_email_teste(email_para: str) -> None:
    nome_projeto = configuracoes.NOME_PROJETO
    assunto = f"{nome_projeto} - Email de teste"
    with open(Path(configuracoes.DIR_MODELOS_EMAIL) / "test_email.html") as f:
        modelo_str = f.read()
    enviar_email(
        email_para=email_para,
        modelo_assunto=assunto,
        modelo_html=modelo_str,
        environment={"project_name": configuracoes.NOME_PROJETO, "email": email_para},
    )


def enviar_email_redefinicao_senha(email_para: str, email: str, token: str) -> None:
    nome_projeto = configuracoes.NOME_PROJETO
    assunto = f"{nome_projeto} - Recuperação de senha para o usuário {email}"
    with open(Path(configuracoes.DIR_MODELOS_EMAIL) / "reset_password.html") as f:
        modelo_str = f.read()
    servidor_host = configuracoes.SERVIDOR_HOST
    link = f"{servidor_host}/redefinir-senha?token={token}"
    enviar_email(
        email_para=email_para,
        modelo_assunto=assunto,
        modelo_html=modelo_str,
        environment={
            "project_name": configuracoes.NOME_PROJETO,
            "username": email,
            "email": email_para,
            "valid_hours": configuracoes.HORAS_EXPIRACAO_TOKEN_REDEFINICAO_EMAIL,
            "link": link,
        },
    )


def enviar_email_nova_conta(email_para: str, nome_usuario: str, senha: str) -> None:
    nome_projeto = configuracoes.NOME_PROJETO
    assunto = f"{nome_projeto} - Nova conta para usuário {nome_usuario}"
    with open(Path(configuracoes.DIR_MODELOS_EMAIL) / "new_account.html") as f:
        modelo_str = f.read()
    link = configuracoes.SERVIDOR_HOST
    enviar_email(
        email_para=email_para,
        modelo_assunto=assunto,
        modelo_html=modelo_str,
        environment={
            "project_name": configuracoes.NOME_PROJETO,
            "username": nome_usuario,
            "password": senha,
            "email": email_para,
            "link": link,
        },
    )


def gerar_token_redefinicao_senha(email: str) -> str:
    delta = timedelta(hours=configuracoes.HORAS_EXPIRACAO_TOKEN_REDEFINICAO_EMAIL)
    agora = datetime.utcnow()
    expira = agora + delta
    exp = expira.timestamp()
    jwt_codificado = jwt.encode(
        {"exp": exp, "nbf": agora, "sub": email},
        configuracoes.CHAVE_SECRETA,
        algorithm="HS256",
    )
    return jwt_codificado


def verificar_token_redefinicao_senha(token: str) -> Optional[str]:
    try:
        token_decodificado = jwt.decode(
            token, configuracoes.CHAVE_SECRETA, algorithms=["HS256"]
        )
        return token_decodificado["sub"]
    except jwt.JWTError:
        return None
