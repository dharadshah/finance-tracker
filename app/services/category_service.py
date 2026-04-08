import logging
from sqlalchemy.orm import Session
from app.repository import category_repository
from app.schemas import CategoryCreate
from app.exceptions.finance_exceptions import (
    CategoryNotFoundException,
    CategoryAlreadyExistsException
)
from app.constants.app_constants import DEFAULT_CATEGORIES

logger = logging.getLogger(__name__)


def create_category(db: Session, category: CategoryCreate):
    existing = category_repository.get_category_by_name(db, category.name)
    if existing:
        raise CategoryAlreadyExistsException(category.name)
    return category_repository.create_category(db, category)


def get_categories(db: Session):
    return category_repository.get_categories(db)


def get_category(db: Session, category_id: int):
    category = category_repository.get_category(db, category_id)
    if not category:
        raise CategoryNotFoundException(category_id)
    return category


def delete_category(db: Session, category_id: int):
    category = category_repository.get_category(db, category_id)
    if not category:
        raise CategoryNotFoundException(category_id)
    category_repository.delete_category(db, category_id)


def seed_default_categories(db: Session):
    logger.info("Seeding default categories")
    for item in DEFAULT_CATEGORIES:
        existing = category_repository.get_category_by_name(db, item.value)
        if not existing:
            category_repository.create_category(db, CategoryCreate(name=item.value))
            logger.info(f"Seeded category: {item.value}")