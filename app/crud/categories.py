import logging
from sqlalchemy.orm import Session
from app import models
from app.schemas import CategoryCreate

logger = logging.getLogger(__name__)


def create_category(db: Session, category: CategoryCreate):
    db_category = models.Category(
        name        = category.name,
        description = category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    logger.info(f"Category created: {db_category.name}")
    return db_category


def get_categories(db: Session):
    logger.info("Fetching all categories")
    return db.query(models.Category).all()


def get_category(db: Session, category_id: int):
    logger.info(f"Fetching category id: {category_id}")
    return db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()


def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(
        models.Category.name == name
    ).first()


def delete_category(db: Session, category_id: int):
    category = get_category(db, category_id)
    if category:
        db.delete(category)
        db.commit()
        logger.info(f"Category deleted: {category_id}")
        return True
    logger.warning(f"Category not found: {category_id}")
    return False