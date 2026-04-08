import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.config.database_config import get_db
from app.services import category_service
from app.schemas import CategoryCreate, CategoryResponse

from app.constants.app_constants import ROUTE_CONSTANTS


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = ROUTE_CONSTANTS.CATEGORIES_PREFIX.value,
    tags   = ["Categories"]
)


@router.post("", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    return category_service.create_category(db, category)


@router.get("", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    return category_service.get_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    return category_service.get_category(db, category_id)


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category_service.delete_category(db, category_id)
    return {"message": "Category deleted successfully"}