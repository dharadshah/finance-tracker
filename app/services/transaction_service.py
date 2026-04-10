import logging
from sqlalchemy.orm import Session
from app.repository import transaction_repository
from app.schemas import TransactionCreate
from app.schemas.transaction_schema import TransactionResponse
from app.exceptions.app_exceptions import NotFoundError, InternalError

logger = logging.getLogger(__name__)


def create_transaction(db: Session, transaction: TransactionCreate):
    try:
        result = transaction_repository.create_transaction(db, transaction)
        return TransactionResponse.from_orm_with_rel(result)
    except Exception as e:
        logger.error(f"Failed to create transaction: {e}")
        raise InternalError(f"Failed to create transaction: {str(e)}")


def bulk_create_transactions(db: Session, transactions: list):
    """Create multiple transactions atomically."""
    try:
        results = transaction_repository.bulk_create_transactions(db, transactions)
        return [TransactionResponse.from_orm_with_rel(t) for t in results]
    except Exception as e:
        logger.error(f"Bulk create failed: {e}")
        raise InternalError(f"Bulk create failed: {str(e)}")


def get_transactions(db: Session):
    transactions = transaction_repository.get_transactions(db)
    return [TransactionResponse.from_orm_with_rel(t) for t in transactions]


def get_transactions_filtered(
    db          : Session,
    is_expense  : bool  = None,
    min_amount  : float = None,
    max_amount  : float = None,
    category_id : int   = None
):
    transactions = transaction_repository.get_transactions_filtered(
        db, is_expense, min_amount, max_amount, category_id
    )
    return [TransactionResponse.from_orm_with_rel(t) for t in transactions]


def get_transaction(db: Session, transaction_id: int):
    transaction = transaction_repository.get_transaction(db, transaction_id)
    if not transaction:
        raise NotFoundError(f"Transaction with id {transaction_id} not found")
    return TransactionResponse.from_orm_with_rel(transaction)


def update_transaction(db: Session, transaction_id: int, data: TransactionCreate):
    updated = transaction_repository.update_transaction(db, transaction_id, data)
    if not updated:
        raise NotFoundError(f"Transaction with id {transaction_id} not found")
    return TransactionResponse.from_orm_with_rel(updated)


def delete_transaction(db: Session, transaction_id: int):
    deleted = transaction_repository.delete_transaction(db, transaction_id)
    if not deleted:
        raise NotFoundError(f"Transaction with id {transaction_id} not found")
    return deleted


def get_summary(db: Session) -> dict:
    return transaction_repository.get_summary(db)


def get_category_breakdown(db: Session) -> list:
    return transaction_repository.get_category_breakdown(db)