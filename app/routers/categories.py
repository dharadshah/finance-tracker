import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database_config import get_db
from app.crud import categories as crud_categories
from app.schemas import CategoryCreate, CategoryResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post("", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    existing = crud_categories.get_category_by_name(db, category.name)
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    return crud_categories.create_category(db, category)


@router.get("", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    return crud_categories.get_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = crud_categories.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    deleted = crud_categories.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}