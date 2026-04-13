import logging
from functools import lru_cache
from app.config.settings import Settings
from app.config.database_config import SessionLocal
from fastapi import Header
from typing import Optional
import uuid

logger = logging.getLogger("app.dependencies")


def get_db():
    db = SessionLocal()
    try:
        logger.info("Database session opened")
        yield db
    finally:
        db.close()
        logger.info("Database session closed")


@lru_cache
def get_settings() -> Settings:
    logger.info("Loading settings")
    return Settings()


def get_request_id(
    x_request_id: Optional[str] = Header(default=None)
) -> str:
    return x_request_id or str(uuid.uuid4())