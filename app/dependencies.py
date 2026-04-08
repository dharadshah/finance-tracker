import logging
from functools import lru_cache
from sqlalchemy.orm import Session
from app.config.settings import Settings
from app.config.database_config import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)