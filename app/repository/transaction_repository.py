import logging
from sqlalchemy.orm import Session, joinedload
from app.models import Transaction
from app.schemas import TransactionCreate

logger = logging.getLogger(__name__)


def create_transaction(db: Session, transaction: TransactionCreate):
    db_transaction = Transaction(
        description = transaction.description,
        amount      = transaction.amount,
        is_expense  = transaction.is_expense,
        category_id = transaction.category_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    logger.info(f"Transaction created: {db_transaction.id}")
    return db_transaction


def get_transactions(db: Session):
    return db.query(Transaction).options(
        joinedload(Transaction.category_rel)
    ).all()


def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).options(
        joinedload(Transaction.category_rel)
    ).filter(Transaction.id == transaction_id).first()


def get_transactions_by_category(db: Session, category_id: int):
    return db.query(Transaction).options(
        joinedload(Transaction.category_rel)
    ).filter(Transaction.category_id == category_id).all()


def delete_transaction(db: Session, transaction_id: int):
    transaction = get_transaction(db, transaction_id)
    if transaction:
        db.delete(transaction)
        db.commit()
        logger.info(f"Transaction deleted: {transaction_id}")
        return True
    return False


def update_transaction(db: Session, transaction_id: int, data: TransactionCreate):
    transaction = get_transaction(db, transaction_id)
    if transaction:
        transaction.description = data.description
        transaction.amount      = data.amount
        transaction.is_expense  = data.is_expense
        transaction.category_id = data.category_id
        db.commit()
        db.refresh(transaction)
        logger.info(f"Transaction updated: {transaction_id}")
        return transaction
    return None