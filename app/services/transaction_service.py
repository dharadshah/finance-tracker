import logging
from sqlalchemy.orm import Session
from app.repository import transaction_repository
from app.schemas import TransactionCreate
from app.schemas.transaction_schema import TransactionResponse
from app.exceptions.finance_exceptions import TransactionNotFoundException

logger = logging.getLogger(__name__)


def create_transaction(db: Session, transaction: TransactionCreate):
    result = transaction_repository.create_transaction(db, transaction)
    return TransactionResponse.from_orm_with_rel(result)


def get_transactions(db: Session):
    transactions = transaction_repository.get_transactions(db)
    return [TransactionResponse.from_orm_with_rel(t) for t in transactions]


def get_transaction(db: Session, transaction_id: int):
    transaction = transaction_repository.get_transaction(db, transaction_id)
    if not transaction:
        raise TransactionNotFoundException(transaction_id)
    return TransactionResponse.from_orm_with_rel(transaction)


def update_transaction(db: Session, transaction_id: int, data: TransactionCreate):
    updated = transaction_repository.update_transaction(db, transaction_id, data)
    if not updated:
        raise TransactionNotFoundException(transaction_id)
    return TransactionResponse.from_orm_with_rel(updated)


def delete_transaction(db: Session, transaction_id: int):
    deleted = transaction_repository.delete_transaction(db, transaction_id)
    if not deleted:
        raise TransactionNotFoundException(transaction_id)
    return deleted