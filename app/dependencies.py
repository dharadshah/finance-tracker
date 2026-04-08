import logging
from functools import lru_cache
from sqlalchemy.orm import Session
from app.config.settings import Settings
from app.config.database_config import SessionLocal

logger = logging.getLogger(__name__)


# --- Database Dependency ---

def get_db():
    db = SessionLocal()
    try:
        logger.info("Database session opened")
        yield db
    finally:
        db.close()
        logger.info("Database session closed")


# --- Settings Dependency ---

@lru_cache
def get_settings() -> Settings:
    logger.info("Loading settings")
    return Settings()


# --- Logger Dependency ---

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)