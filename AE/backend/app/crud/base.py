from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


def get_dict_from_pydantic(obj: BaseModel) -> dict:
    """Extract dict from Pydantic model regardless of version."""
    if hasattr(obj, "model_dump"):
        # Pydantic V2
        return obj.model_dump()
    # Pydantic V1
    return dict(obj)


def exclude_unset_from_pydantic(obj: BaseModel) -> dict:
    """Get dict with only set fields from Pydantic model."""
    if hasattr(obj, "model_dump"):
        # Pydantic V2
        return obj.model_dump(exclude_unset=True)
    # Pydantic V1
    return obj.dict(exclude_unset=True)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to create, read, update, delete (CRUD).

        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_by(self, db: AsyncSession, **kwargs) -> Optional[ModelType]:
        """Get a single record by arbitrary filters."""
        query = select(self.model)
        for key, value in kwargs.items():
            query = query.where(getattr(self.model, key) == value)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        obj_in_data = get_dict_from_pydantic(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_many(
        self, db: AsyncSession, *, obj_in_list: List[CreateSchemaType]
    ) -> List[ModelType]:
        """Create multiple records at once."""
        db_objs = []
        for obj_in in obj_in_list:
            obj_in_data = get_dict_from_pydantic(obj_in)
            db_obj = self.model(**obj_in_data)
            db_objs.append(db_obj)

        db.add_all(db_objs)
        await db.commit()

        # Refresh all objects
        for db_obj in db_objs:
            await db.refresh(db_obj)

        return db_objs

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update a record."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = exclude_unset_from_pydantic(obj_in)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType:
        """Delete a record."""
        obj = await db.get(self.model, id)
        await db.delete(obj)
        await db.commit()
        return obj
