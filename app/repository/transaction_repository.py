"""Transaction repository - database operations for Transaction model."""
import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, case, literal_column
from typing import List, Optional
from app.repository.base_repository import BaseRepository
from app.models import Transaction, Category
from app.schemas import TransactionCreate

logger = logging.getLogger("app.repository.TransactionRepository")


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction database operations."""

    def __init__(self, db: Session):
        super().__init__(Transaction, db)

    def _query_with_category(self):
        """Base query with category relationship loaded."""
        return self.db.query(Transaction).options(
            joinedload(Transaction.category_rel)
        )

    def create(self, transaction: TransactionCreate) -> Transaction:
        """Create a new transaction.

        Args:
            transaction: TransactionCreate schema.

        Returns:
            Created Transaction with category loaded.
        """
        db_transaction = Transaction(
            description = transaction.description,
            amount      = transaction.amount,
            is_expense  = transaction.is_expense,
            category_id = transaction.category_id
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)

        transaction_id = db_transaction.id
        self.db.expunge(db_transaction)

        return self.get_by_id_with_category(transaction_id)

    def bulk_create(self, transactions: list) -> List[Transaction]:
        """Create multiple transactions atomically.

        Args:
            transactions: List of TransactionCreate schemas.

        Returns:
            List of created Transaction models.
        """
        created = []
        try:
            for data in transactions:
                t = Transaction(
                    description = data.description,
                    amount      = data.amount,
                    is_expense  = data.is_expense,
                    category_id = data.category_id
                )
                self.db.add(t)
                created.append(t)

            self.db.commit()
            self.logger.info(f"Bulk created {len(created)} transactions")
            return [self.get_by_id_with_category(t.id) for t in created]

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Bulk create failed, rolled back: {e}")
            raise

    def get_by_id_with_category(self, transaction_id: int) -> Optional[Transaction]:
        """Fetch a transaction by id with category loaded.

        Args:
            transaction_id: Transaction primary key.

        Returns:
            Transaction with category_rel loaded.
        """
        return self._query_with_category().filter(
            Transaction.id == transaction_id
        ).first()

    def get_all_with_category(self) -> List[Transaction]:
        """Fetch all transactions with categories loaded."""
        return self._query_with_category().order_by(
            desc(Transaction.id)
        ).all()

    def get_filtered(
        self,
        is_expense  : bool  = None,
        min_amount  : float = None,
        max_amount  : float = None,
        category_id : int   = None,
        limit       : int   = 10,
        offset      : int   = 0
    ) -> List[Transaction]:
        """Fetch transactions with dynamic ORM filters.

        Args:
            is_expense  : Filter by expense or income.
            min_amount  : Minimum amount filter.
            max_amount  : Maximum amount filter.
            category_id : Filter by category.
            limit       : Max results to return.
            offset      : Pagination offset.

        Returns:
            Filtered list of transactions.
        """
        query = self._query_with_category()

        if is_expense is not None:
            query = query.filter(Transaction.is_expense == is_expense)
        if min_amount is not None:
            query = query.filter(Transaction.amount >= min_amount)
        if max_amount is not None:
            query = query.filter(Transaction.amount <= max_amount)
        if category_id is not None:
            query = query.filter(Transaction.category_id == category_id)

        return query.order_by(
            desc(Transaction.amount)
        ).offset(offset).limit(limit).all()

    def get_transactions_by_category(self, category_id: int) -> List[Transaction]:
        """Fetch all transactions for a specific category.

        Args:
            category_id: Category primary key.

        Returns:
            List of transactions in that category.
        """
        return self._query_with_category().filter(
            Transaction.category_id == category_id
        ).all()

    def update(self, transaction_id: int, data: TransactionCreate) -> Optional[Transaction]:
        """Update a transaction.

        Args:
            transaction_id: Transaction primary key.
            data          : Updated TransactionCreate schema.

        Returns:
            Updated Transaction or None if not found.
        """
        transaction = self.get_by_id_with_category(transaction_id)
        if transaction:
            transaction.description = data.description
            transaction.amount      = data.amount
            transaction.is_expense  = data.is_expense
            transaction.category_id = data.category_id
            self.db.commit()
            self.db.refresh(transaction)
            return self.get_by_id_with_category(transaction_id)
        return None

    def get_summary(self) -> dict:
        """ORM-based financial summary using SQLAlchemy func.

        Uses func.sum with case expressions — ORM layer,
        no raw SQL strings.

        Returns:
            Dict with income, expenses, balance, savings rate.
        """
        result = self.db.query(
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.is_expense == False, Transaction.amount),
                        else_=0
                    )
                ), 0
            ).label("total_income"),
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.is_expense == True, Transaction.amount),
                        else_=0
                    )
                ), 0
            ).label("total_expenses"),
            func.count(Transaction.id).label("transaction_count")
        ).first()

        total_income   = float(result.total_income)
        total_expenses = float(result.total_expenses)
        balance        = total_income - total_expenses
        savings_rate   = round(
            (balance / total_income * 100), 2
        ) if total_income > 0 else 0.0

        return {
            "total_income"      : total_income,
            "total_expenses"    : total_expenses,
            "balance"           : balance,
            "savings_rate"      : savings_rate,
            "transaction_count" : result.transaction_count
        }

    def get_category_breakdown(self) -> list:
        """ORM-based expense breakdown by category using SQLAlchemy func.

        Uses func.count, func.sum, func.avg with ORM join —
        no raw SQL strings.

        Returns:
            List of dicts with category spending breakdown.
        """
        results = self.db.query(
            func.coalesce(Category.name, "Uncategorized").label("category"),
            func.count(Transaction.id).label("transaction_count"),
            func.sum(Transaction.amount).label("total_amount"),
            func.avg(Transaction.amount).label("avg_amount")
        ).outerjoin(
            Category, Transaction.category_id == Category.id
        ).filter(
            Transaction.is_expense == True
        ).group_by(
            Category.name
        ).order_by(
            desc("total_amount")
        ).all()

        return [
            {
                "category"          : row.category,
                "transaction_count" : row.transaction_count,
                "total_amount"      : round(float(row.total_amount), 2),
                "avg_amount"        : round(float(row.avg_amount), 2)
            }
            for row in results
        ]