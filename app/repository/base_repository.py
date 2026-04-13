"""Abstract base repository with common database operations."""
import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from app.config.database_config import Base

logger = logging.getLogger("app.models.transaction")

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """Base repository providing common CRUD operations.

    Type Parameters:
        ModelType: The SQLAlchemy model this repository manages.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """Initialize with model class and database session.

        Args:
            model: SQLAlchemy model class.
            db   : Database session.
        """
        self.model  = model
        self.db     = db
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        self.logger.info(f"Fetching {self.model.__name__} id: {id}")
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[ModelType]:
        """Fetch all records."""
        self.logger.info(f"Fetching all {self.model.__name__}")
        return self.db.query(self.model).all()

    def delete(self, id: int) -> bool:
        """Delete a record by primary key."""
        record = self.get_by_id(id)
        if record:
            self.db.delete(record)
            self.db.commit()
            self.logger.info(f"Deleted {self.model.__name__} id: {id}")
            return True
        self.logger.warning(f"{self.model.__name__} id {id} not found for delete")
        return False

    def save(self, record: ModelType) -> ModelType:
        """Add and commit a new record."""
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        self.logger.info(f"Saved {self.model.__name__} id: {record.id}")
        return record