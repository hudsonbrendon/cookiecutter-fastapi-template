from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import configuracoes
from app.utils import enviar_email_nova_conta

router = APIRouter()


@router.get("/", response_model=List[schemas.Usuario])
def listar_usuarios(
    db: Session = Depends(deps.obter_db),
    pular: int = 0,
    limite: int = 100,
    _: models.Usuario = Depends(deps.obter_superusuario_atual),
) -> Any:
    """Lista todos os usuários.

    Args:
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).
        pular (int, optional): O número de registros a pular. Padrão é 0.
        limite (int, optional): O número de registros a retornar. Padrão é 100.
        _ (models.Usuario, optional): O usuário atual. Padrão é Depends(deps.obter_superusuario_atual).

    Raises:
        HTTPException: Não foi possível validar as credenciais.

    Returns:
        Any: A lista de usuários.
    """
    usuarios = crud.usuario.obter_multiplos(db, skip=pular, limit=limite)
    return usuarios


@router.post("/", response_model=schemas.Usuario)
def criar_usuario(
    *,
    db: Session = Depends(deps.obter_db),
    usuario_in: schemas.CriarUsuario,
    _: models.Usuario = Depends(deps.obter_superusuario_atual),
) -> Any:
    """Criar um novo usuário.

    Args:
        usuario_in (schemas.CriarUsuario): Os dados do usuário.
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).
        _ (models.Usuario, optional): O usuário atual. Padrão é Depends(deps.obter_superusuario_atual).

    Raises:
        HTTPException: Não foi possível validar as credenciais.

    Returns:
        Any: O novo usuário.
    """
    usuario = crud.usuario.obter_por_email(db, email=usuario_in.email)
    if usuario:
        raise HTTPException(
            status_code=400,
            detail="O usuário com este nome de usuário já existe no sistema.",
        )
    usuario = crud.usuario.criar(db, obj_in=usuario_in)
    if configuracoes.EMAILS_HABILITADOS and usuario_in.email:
        enviar_email_nova_conta(
            email_para=usuario_in.email,
            nome_usuario=usuario_in.email,
            senha=usuario_in.senha,
        )
    return usuario


@router.put("/eu", response_model=schemas.Usuario)
def atualizar_usuario_eu(
    *,
    db: Session = Depends(deps.obter_db),
    primeiro_nome: str = Body(None),
    sobrenome: str = Body(None),
    cpf: str = Body(None),
    telefone: str = Body(None),
    senha: str = Body(None),
    email: EmailStr = Body(None),
    usuario_atual: models.Usuario = Depends(deps.obter_usuario_ativo_atual),
) -> Any:
    """Atualizar o usuário atual.

    Args:
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).
        primeiro_nome (str, optional): O primeiro nome. Padrão é Body(None).
        sobrenome (str, optional): O sobrenome. Padrão é Body(None).
        cpf (str, optional): O CPF. Padrão é Body(None).
        telefone (str, optional): O número de telefone. Padrão é Body(None).
        senha (str, optional): A senha. Padrão é Body(None).
        email (EmailStr, optional): O email. Padrão é Body(None).
        usuario_atual (models.Usuario, optional): O usuário atual. Padrão é Depends(deps.obter_usuario_ativo_atual).

    Raises:
        HTTPException: Não foi possível validar as credenciais.

    Returns:
        Any: O usuário atualizado.
    """
    dados_usuario_atual = jsonable_encoder(usuario_atual)
    usuario_in = schemas.AtualizarUsuario(**dados_usuario_atual)

    if primeiro_nome is not None:
        usuario_in.primeiro_nome = primeiro_nome
    if sobrenome is not None:
        usuario_in.sobrenome = sobrenome
    if cpf is not None:
        usuario_in.cpf = cpf
    if email is not None:
        usuario_in.email = email
    if telefone is not None:
        usuario_in.telefone = telefone
    if senha is not None:
        usuario_in.senha = senha

    usuario = crud.usuario.atualizar(db, db_obj=usuario_atual, obj_in=usuario_in)
    return usuario


@router.get("/eu", response_model=schemas.Usuario)
def ler_usuario_eu(
    db: Session = Depends(deps.obter_db),
    usuario_atual: models.Usuario = Depends(deps.obter_usuario_ativo_atual),
) -> Any:
    """Obter o usuário atual.

    Args:
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).
        usuario_atual (models.Usuario, optional): O usuário atual. Padrão é Depends(deps.obter_usuario_ativo_atual).

    Raises:
        HTTPException: Não foi possível validar as credenciais.

    Returns:
        Any: O usuário atual.
    """
    return usuario_atual


@router.post("/aberto", response_model=schemas.Usuario)
def criar_usuario_aberto(
    *,
    db: Session = Depends(deps.obter_db),
    primeiro_nome: str = Body(None),
    sobrenome: str = Body(None),
    cpf: str = Body(...),
    email: EmailStr = Body(...),
    telefone: str = Body(...),
    senha: str = Body(...),
) -> Any:
    """Criar um novo usuário sem a necessidade de estar logado.

    Args:
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).
        primeiro_nome (str, optional): O nome completo. Padrão é Body(...).
        sobrenome (str, optional): O sobrenome. Padrão é Body(...).
        cpf (str, optional): O CPF. Padrão é Body(...).
        email (EmailStr, optional): O email. Padrão é Body(...).
        telefone (str, optional): O número de telefone. Padrão é Body(...).
        senha (str, optional): A senha. Padrão é Body(...).

    Raises:
        HTTPException: O registro aberto de usuários é proibido neste servidor.

    Returns:
        Any: O novo usuário.
    """
    if not configuracoes.REGISTRO_USUARIOS_ABERTO:
        raise HTTPException(
            status_code=403,
            detail="O registro aberto de usuários é proibido neste servidor.",
        )
    usuario = crud.usuario.obter_por_email(db, email=email)
    if usuario:
        raise HTTPException(
            status_code=400,
            detail="O usuário com este nome de usuário já existe no sistema.",
        )
    usuario_in = schemas.CriarUsuario(
        primeiro_nome=primeiro_nome,
        sobrenome=sobrenome,
        cpf=cpf,
        email=email,
        telefone=telefone,
        permissao=models.EnumPermissaoUsuario.USUARIO.value,
        senha=senha,
    )
    usuario = crud.usuario.criar(db, obj_in=usuario_in)
    return usuario


@router.get("/{id_usuario}", response_model=schemas.Usuario)
def ler_usuario_por_id(
    id_usuario: int,
    usuario_atual: models.Usuario = Depends(deps.obter_usuario_ativo_atual),
    db: Session = Depends(deps.obter_db),
) -> Any:
    """Obter um usuário específico por ID.

    Args:
        id_usuario (int): O ID do usuário.
        usuario_atual (models.Usuario, optional): O usuário atual. Padrão é Depends(deps.obter_usuario_ativo_atual).
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).

    Raises:
        HTTPException: O usuário não tem privilégios suficientes.

    Returns:
        Any: O usuário.
    """
    usuario = crud.usuario.obter(db, id=id_usuario)
    if usuario == usuario_atual:
        return usuario
    if not crud.usuario.eh_superusuario(usuario_atual):
        raise HTTPException(
            status_code=400,
            detail="O usuário não tem privilégios suficientes.",
        )
    return usuario


@router.put("/{id_usuario}", response_model=schemas.Usuario)
def atualizar_usuario(
    *,
    db: Session = Depends(deps.obter_db),
    id_usuario: int,
    usuario_in: schemas.AtualizarUsuario,
    _: models.Usuario = Depends(deps.obter_superusuario_atual),
) -> Any:
    """Atualizar um usuário.

    Args:
        id_usuario (int): O ID do usuário.
        usuario_in (schemas.AtualizarUsuario): Os dados do usuário.
        db (Session, optional): A sessão do banco de dados. Padrão é Depends(deps.obter_db).
        _ (models.Usuario, optional): O usuário atual. Padrão é Depends(deps.obter_superusuario_atual).

    Raises:
        HTTPException: Não foi possível validar as credenciais.

    Returns:
        Any: O usuário atualizado.
    """
    usuario = crud.usuario.obter(db, id=id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="O usuário com este nome de usuário não existe no sistema.",
        )
    usuario = crud.usuario.atualizar(db, db_obj=usuario, obj_in=usuario_in)
    return usuario
