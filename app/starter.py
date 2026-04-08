import logging
from fastapi import FastAPI
from app.config.settings import settings
from app.config.logging_config import setup_logging
from app.config.database_config import engine, SessionLocal
from app.config.database_config import Base
from app.routers import transactions, categories
from app import health
from app.services.category_service import seed_default_categories
from app.exceptions.handlers import register_exception_handlers


setup_logging()

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    # Seed default categories on startup
    db = SessionLocal()
    try:
        seed_default_categories(db)
    finally:
        db.close()

    app = FastAPI(
        title   = settings.app_name,
        version = settings.app_version
    )

    app.include_router(health.router)
    app.include_router(transactions.router)
    app.include_router(categories.router)

    logger.info(f"{settings.app_name} started successfully")

    return app