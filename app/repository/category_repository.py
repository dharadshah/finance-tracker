import logging
from sqlalchemy.orm import Session
from app.models import Category
from app.schemas import CategoryCreate
from app.dependencies import get_logger

logger = get_logger("app.repository.category_repository")


def create_category(db: Session, category: CategoryCreate):
    db_category = Category(
        name        = category.name,
        description = category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    logger.info(f"Category created: {db_category.name}")
    return db_category


def get_categories(db: Session):
    return db.query(Category).all()


def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()


def delete_category(db: Session, category_id: int):
    category = get_category(db, category_id)
    if category:
        db.delete(category)
        db.commit()
        logger.info(f"Category deleted: {category_id}")
        return True
    return False