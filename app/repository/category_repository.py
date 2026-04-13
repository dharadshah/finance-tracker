"""Category repository - database operations for Category model."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.repository.base_repository import BaseRepository
from app.models import Category
from app.schemas import CategoryCreate


class CategoryRepository(BaseRepository[Category]):
    """Repository for Category database operations."""

    def __init__(self, db: Session):
        super().__init__(Category, db)

    def create(self, category: CategoryCreate) -> Category:
        """Create a new category.

        Args:
            category: CategoryCreate schema.

        Returns:
            Created Category model.
        """
        db_category = Category(
            name        = category.name,
            description = category.description
        )
        return self.save(db_category)

    def get_by_name(self, name: str) -> Optional[Category]:
        """Fetch a category by name.

        Args:
            name: Category name to search.

        Returns:
            Category if found, None otherwise.
        """
        return self.db.query(Category).filter(
            Category.name == name
        ).first()

    def get_all_categories(self) -> List[Category]:
        """Fetch all categories."""
        return self.get_all()