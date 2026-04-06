import logging
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from config.database_config import Base

logger = logging.getLogger(__name__)


class Category(Base):
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="category_rel")


class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount      = Column(Float, nullable=False)
    is_expense  = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    category_rel = relationship("Category", back_populates="transactions")