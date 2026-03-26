import logging
from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base

logger = logging.getLogger(__name__)


class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    amount      = Column(Float, nullable=False)
    is_expense  = Column(Boolean, default=True)
    category    = Column(String, nullable=True)