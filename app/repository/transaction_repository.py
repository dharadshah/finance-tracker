import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, and_, or_, desc, func
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

    transaction_id = db_transaction.id
    db.expunge(db_transaction)

    return get_transaction(db, transaction_id)


def bulk_create_transactions(db: Session, transactions_data: list):
    """Create multiple transactions in one atomic operation.
    All succeed or all fail together.
    """
    created = []
    try:
        for data in transactions_data:
            t = Transaction(
                description = data.description,
                amount      = data.amount,
                is_expense  = data.is_expense,
                category_id = data.category_id
            )
            db.add(t)
            created.append(t)

        db.commit()
        logger.info(f"Bulk created {len(created)} transactions")

        # re-fetch all with relationships
        return [get_transaction(db, t.id) for t in created]

    except Exception as e:
        db.rollback()
        logger.error(f"Bulk create failed, rolled back: {e}")
        raise


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


def get_transactions_filtered(
    db          : Session,
    is_expense  : bool  = None,
    min_amount  : float = None,
    max_amount  : float = None,
    category_id : int   = None,
    limit       : int   = 10,
    offset      : int   = 0
):
    query = db.query(Transaction).options(
        joinedload(Transaction.category_rel)
    )

    if is_expense is not None:
        query = query.filter(Transaction.is_expense == is_expense)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)

    return query.order_by(desc(Transaction.amount)).offset(offset).limit(limit).all()

def get_summary(db: Session) -> dict:
    """Native SQL query for financial summary."""
    result = db.execute(
        text("""
            SELECT
                COALESCE(SUM(CASE WHEN is_expense = 0 THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN is_expense = 1 THEN amount ELSE 0 END), 0) as total_expenses,
                COUNT(id) as transaction_count
            FROM transactions
        """)
    ).mappings().first()

    total_income   = float(result["total_income"])
    total_expenses = float(result["total_expenses"])
    balance        = total_income - total_expenses
    savings_rate   = round((balance / total_income * 100), 2) if total_income > 0 else 0.0

    return {
        "total_income"      : total_income,
        "total_expenses"    : total_expenses,
        "balance"           : balance,
        "savings_rate"      : savings_rate,
        "transaction_count" : result["transaction_count"]
    }


def get_category_breakdown(db: Session) -> list:
    """Native SQL aggregation by category."""
    result = db.execute(
        text("""
            SELECT
                COALESCE(c.name, 'Uncategorized') as category,
                COUNT(t.id)                        as transaction_count,
                SUM(t.amount)                      as total_amount,
                AVG(t.amount)                      as avg_amount
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.is_expense = 1
            GROUP BY c.name
            ORDER BY total_amount DESC
        """)
    ).mappings().all()

    return [
        {
            "category"          : row["category"],
            "transaction_count" : row["transaction_count"],
            "total_amount"      : round(float(row["total_amount"]), 2),
            "avg_amount"        : round(float(row["avg_amount"]), 2)
        }
        for row in result
    ]


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
        return get_transaction(db, transaction_id)
    return None