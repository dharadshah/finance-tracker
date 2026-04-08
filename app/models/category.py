import logging
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database_config import Base

logger = logging.getLogger(__name__)


class Category(Base):
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="category_rel")