"""Category service - business logic for category operations."""
import logging
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from app.repository.category_repository import CategoryRepository
from app.schemas import CategoryCreate, CategoryResponse
from app.exceptions.app_exceptions import NotFoundError, ConflictError
from app.constants.app_constants import DEFAULT_CATEGORIES

logger = logging.getLogger(__name__)


class CategoryService(BaseService):
    """Service handling all category business logic."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = CategoryRepository(db)

    def create(self, category: CategoryCreate) -> CategoryResponse:
        """Create a new category.

        Args:
            category: CategoryCreate schema.

        Returns:
            CategoryResponse schema.

        Raises:
            ConflictError: If category name already exists.
        """
        existing = self.repository.get_by_name(category.name)
        if existing:
            raise ConflictError(f"Category '{category.name}' already exists")
        result = self.repository.create(category)
        self.logger.info(f"Category created: {result.name}")
        return result

    def get_all(self):
        """Fetch all categories."""
        return self.repository.get_all_categories()

    def get_by_id(self, category_id: int):
        """Fetch a category by id.

        Raises:
            NotFoundError: If category not found.
        """
        category = self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundError(f"Category with id {category_id} not found")
        return category

    def delete(self, category_id: int):
        """Delete a category by id.

        Raises:
            NotFoundError: If category not found.
        """
        self.get_by_id(category_id)
        self.repository.delete(category_id)
        self.logger.info(f"Category deleted: {category_id}")

    def seed_defaults(self):
        """Seed default categories if they do not exist."""
        self.logger.info("Seeding default categories")
        for item in DEFAULT_CATEGORIES:
            existing = self.repository.get_by_name(item.value)
            if not existing:
                self.repository.create(CategoryCreate(name=item.value))
                self.logger.info(f"Seeded: {item.value}")