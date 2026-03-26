import logging
from sqlalchemy.orm import Session
from app import models
from app.schemas import TransactionCreate

logger = logging.getLogger(__name__)


def create_transaction(db: Session, transaction: TransactionCreate):
    db_transaction = models.Transaction(
        description=transaction.description,
        amount=transaction.amount,
        is_expense=transaction.is_expense,
        category=transaction.category
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    logger.info(f"Transaction created with id: {db_transaction.id}")
    return db_transaction


def get_transactions(db: Session):
    logger.info("Fetching all transactions")
    return db.query(models.Transaction).all()


def get_transaction(db: Session, transaction_id: int):
    logger.info(f"Fetching transaction id: {transaction_id}")
    return db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()


def delete_transaction(db: Session, transaction_id: int):
    transaction = get_transaction(db, transaction_id)
    if transaction:
        db.delete(transaction)
        db.commit()
        logger.info(f"Transaction deleted: {transaction_id}")
        return True
    logger.warning(f"Transaction not found: {transaction_id}")
    return False


def update_transaction(db: Session, transaction_id: int, data: TransactionCreate):
    transaction = get_transaction(db, transaction_id)
    if transaction:
        transaction.description = data.description
        transaction.amount      = data.amount
        transaction.is_expense  = data.is_expense
        transaction.category    = data.category
        db.commit()
        db.refresh(transaction)
        logger.info(f"Transaction updated: {transaction_id}")
        return transaction
    logger.warning(f"Transaction not found for update: {transaction_id}")
    return None