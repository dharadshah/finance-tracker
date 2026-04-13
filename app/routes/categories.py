"""Category routes for Personal Finance Tracker API."""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from logging import Logger
from typing import List
from app.routes.base_router import BaseRouter
from app.dependencies import get_db, get_settings, get_logger
from app.config.settings import Settings
from app.services.category_service import CategoryService
from app.schemas import CategoryCreate, CategoryResponse
from app.constants.app_constants import ROUTE_CONSTANTS

logger = logging.getLogger(__name__)


class CategoryRouter(BaseRouter):
    """Router handling all category endpoints."""

    def __init__(self):
        super().__init__(
            prefix = ROUTE_CONSTANTS.CATEGORIES_PREFIX.value,
            tags   = ["Categories"]
        )

    def register(self) -> APIRouter:
        """Register all category routes."""

        @self.router.post("", response_model=CategoryResponse)
        async def create_category(
            category : CategoryCreate,
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            self.logger.info(f"Creating category: {category.name}")
            return CategoryService(db).create(category)

        @self.router.get("", response_model=List[CategoryResponse])
        async def get_categories(
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            self.logger.info("Fetching all categories")
            return CategoryService(db).get_all()

        @self.router.get("/{category_id}", response_model=CategoryResponse)
        async def get_category(
            category_id : int,
            db          : Session  = Depends(get_db),
            settings    : Settings = Depends(get_settings)
        ):
            self.logger.info(f"Fetching category: {category_id}")
            return CategoryService(db).get_by_id(category_id)

        @self.router.delete("/{category_id}")
        async def delete_category(
            category_id : int,
            db          : Session  = Depends(get_db),
            settings    : Settings = Depends(get_settings)
        ):
            self.logger.info(f"Deleting category: {category_id}")
            CategoryService(db).delete(category_id)
            return {"message": "Category deleted successfully"}

        return self.router


# module level instance
router = CategoryRouter().register()