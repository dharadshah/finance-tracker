from app.config.logging_config import logger
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config.settings import settings


class Base(DeclarativeBase):
    pass


def create_db_engine(database_url: str):
    """Create a SQLAlchemy engine with foreign key enforcement enabled.

    Args:
        database_url: Database connection URL.

    Returns:
        Configured SQLAlchemy engine.
    """
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


engine        = create_db_engine(settings.database_url)
SessionLocal  = sessionmaker(autocommit=False, autoflush=False, bind=engine)