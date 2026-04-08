import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from logging import Logger
from typing import List
from app.dependencies import get_db, get_settings, get_logger
from app.config.settings import Settings
from app.services import category_service
from app.schemas import CategoryCreate, CategoryResponse
from app.constants.app_constants import ROUTE_CONSTANTS

router = APIRouter(
    prefix = ROUTE_CONSTANTS.CATEGORIES_PREFIX.value,
    tags   = ["Categories"]
)


def get_category_logger() -> Logger:
    return get_logger("app.routes.categories")


@router.post("", response_model=CategoryResponse)
async def create_category(
    category : CategoryCreate,
    db       : Session  = Depends(get_db),
    settings : Settings = Depends(get_settings),
    logger   : Logger   = Depends(get_category_logger)
):
    logger.info(f"Creating category: {category.name}")
    return category_service.create_category(db, category)


@router.get("", response_model=List[CategoryResponse])
async def get_categories(
    db       : Session  = Depends(get_db),
    settings : Settings = Depends(get_settings),
    logger   : Logger   = Depends(get_category_logger)
):
    logger.info("Fetching all categories")
    return category_service.get_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id : int,
    db          : Session  = Depends(get_db),
    settings    : Settings = Depends(get_settings),
    logger      : Logger   = Depends(get_category_logger)
):
    logger.info(f"Fetching category: {category_id}")
    return category_service.get_category(db, category_id)


@router.delete("/{category_id}")
async def delete_category(
    category_id : int,
    db          : Session  = Depends(get_db),
    settings    : Settings = Depends(get_settings),
    logger      : Logger   = Depends(get_category_logger)
):
    logger.info(f"Deleting category: {category_id}")
    category_service.delete_category(db, category_id)
    return {"message": "Category deleted successfully"}