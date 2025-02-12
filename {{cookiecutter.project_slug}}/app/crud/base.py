from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """The CRUD object with default methods to Create, Read, Update, Delete (CRUD) objects.

    Args:
        Generic (_type_): The generic type.

    Returns:
        _type_: The CRUD object.
    """

    def __init__(self, model: Type[ModelType]):
        """Initialize the CRUD object.

        Args:
            model (Type[ModelType]): The model.

        Returns:
            _type_: The CRUD object.
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get an object by ID.

        Args:
            db (Session): The database session.
            id (Any): The object ID.

        Returns:
            Optional[ModelType]: The object.
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get all objects.

        Args:
            db (Session): The database session.
            skip (int, optional): The number of records to skip. Defaults to 0.
            limit (int, optional): The number of records to return. Defaults to 100.

        Returns:
            List[ModelType]: The list of objects.
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new object.

        Args:
            db (Session): The database session.
            obj_in (CreateSchemaType): The object data.

        Returns:
            ModelType: The new object.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update an object.

        Args:
            db (Session): The database session.
            db_obj (ModelType): The object.
            obj_in (Union[UpdateSchemaType, Dict[str, Any]]): The object data.

        Returns:
            ModelType: The updated object.
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

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Remove an object.

        Args:
            db (Session): The database session.
            id (int): The object ID.

        Returns:
            ModelType: The removed object.
        """
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj
