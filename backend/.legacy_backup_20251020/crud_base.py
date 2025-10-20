"""Generic CRUD base class following DRY principles"""
from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD operations base class

    Provides common CRUD operations to reduce code duplication across all entities.
    Follows DRY principle by centralizing common database operations.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model class

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance or None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record

        Args:
            db: Database session
            obj_in: Pydantic schema with creation data

        Returns:
            Created model instance
        """
        obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
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
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record

        Args:
            db: Database session
            db_obj: Existing model instance to update
            obj_in: Pydantic schema or dict with update data

        Returns:
            Updated model instance
        """
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            if field in obj_data:
                setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_by_id(
        self,
        db: Session,
        *,
        id: Any,
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Update a record by ID

        Args:
            db: Database session
            id: Record ID
            obj_in: Update data

        Returns:
            Updated model instance or None if not found
        """
        db_obj = self.get(db, id)
        if db_obj:
            return self.update(db, db_obj=db_obj, obj_in=obj_in)
        return None

    def delete(self, db: Session, *, id: Any) -> bool:
        """
        Delete a record by ID

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    def exists(self, db: Session, *, id: Any) -> bool:
        """
        Check if a record exists

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if exists, False otherwise
        """
        return db.query(self.model).filter(self.model.id == id).first() is not None
