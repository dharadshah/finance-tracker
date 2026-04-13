"""Abstract base service with common business logic patterns."""
import logging
from abc import ABC
from sqlalchemy.orm import Session


class BaseService(ABC):
    """Base service class providing shared patterns for all services.

    Subclasses should:
        - inject their repository in __init__
        - implement domain-specific methods
        - raise appropriate AppError subclasses
    """

    def __init__(self, db: Session):
        """Initialize with database session.

        Args:
            db: SQLAlchemy database session.
        """
        self.db     = db
        self.logger = logging.getLogger(self.__class__.__name__)