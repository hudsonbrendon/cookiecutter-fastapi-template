from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base

TipoModelo = TypeVar("TipoModelo", bound=Base)
TipoEsquemaCriacao = TypeVar("TipoEsquemaCriacao", bound=BaseModel)
TipoEsquemaAtualizacao = TypeVar("TipoEsquemaAtualizacao", bound=BaseModel)


class CRUDBase(Generic[TipoModelo, TipoEsquemaCriacao, TipoEsquemaAtualizacao]):
    """O objeto CRUD com métodos padrão para Criar, Ler, Atualizar, Excluir (CRUD) objetos.

    Args:
        Generic (_type_): O tipo genérico.

    Returns:
        _type_: O objeto CRUD.
    """

    def __init__(self, model: Type[TipoModelo]):
        """Inicializa o objeto CRUD.

        Args:
            model (Type[TipoModelo]): O modelo.

        Returns:
            _type_: O objeto CRUD.
        """
        self.model = model

    def obter(self, db: Session, id: Any) -> Optional[TipoModelo]:
        """Obter um objeto por ID.

        Args:
            db (Session): A sessão do banco de dados.
            id (Any): O ID do objeto.

        Returns:
            Optional[TipoModelo]: O objeto.
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def obter_multiplos(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[TipoModelo]:
        """Obter todos os objetos.

        Args:
            db (Session): A sessão do banco de dados.
            skip (int, optional): O número de registros a pular. Padrão é 0.
            limit (int, optional): O número de registros a retornar. Padrão é 100.

        Returns:
            List[TipoModelo]: A lista de objetos.
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def criar(self, db: Session, *, obj_in: TipoEsquemaCriacao) -> TipoModelo:
        """Criar um novo objeto.

        Args:
            db (Session): A sessão do banco de dados.
            obj_in (TipoEsquemaCriacao): Os dados do objeto.

        Returns:
            TipoModelo: O novo objeto.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def atualizar(
        self,
        db: Session,
        *,
        db_obj: TipoModelo,
        obj_in: Union[TipoEsquemaAtualizacao, Dict[str, Any]],
    ) -> TipoModelo:
        """Atualizar um objeto.

        Args:
            db (Session): A sessão do banco de dados.
            db_obj (TipoModelo): O objeto.
            obj_in (Union[TipoEsquemaAtualizacao, Dict[str, Any]]): Os dados do objeto.

        Returns:
            TipoModelo: O objeto atualizado.
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remover(self, db: Session, *, id: int) -> TipoModelo:
        """Remover um objeto.

        Args:
            db (Session): A sessão do banco de dados.
            id (int): O ID do objeto.

        Returns:
            TipoModelo: O objeto removido.
        """
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj
