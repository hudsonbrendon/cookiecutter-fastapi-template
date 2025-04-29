"""Este módulo é responsável por inicializar o banco de dados."""

from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import configuracoes
from app.core.enums import EnumPermissaoUsuario
from app.tests.utils.utils import cpf_aleatorio, telefone_aleatorio


def iniciar_db(db: Session) -> None:
    """Inicializa o banco de dados."""
    # Tabelas devem ser criadas com migrações do Alembic
    # Mas se você não quiser usar migrações, crie
    # as tabelas descomentando a próxima linha
    # Base.metadata.create_all(bind=engine)

    usuario = crud.usuario.obter_por_email(
        db, email=configuracoes.PRIMEIRO_SUPERUSUARIO
    )

    if not usuario:
        usuario_in = schemas.CriarUsuario(
            email=configuracoes.PRIMEIRO_SUPERUSUARIO,
            telefone=telefone_aleatorio(),
            cpf=cpf_aleatorio(),
            permissao=EnumPermissaoUsuario.ADMINISTRADOR.value,
            senha=configuracoes.SENHA_PRIMEIRO_SUPERUSUARIO,
            eh_superusuario=True,
        )
        crud.usuario.criar(db, obj_in=usuario_in)
