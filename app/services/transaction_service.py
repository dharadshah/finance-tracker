"""Transaction service - business logic for transaction operations."""
import logging
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from app.repository.transaction_repository import TransactionRepository
from app.schemas import TransactionCreate
from app.schemas.transaction_schema import TransactionResponse, BulkTransactionCreate
from app.exceptions.app_exceptions import NotFoundError, InternalError

logger = logging.getLogger(__name__)


class TransactionService(BaseService):
    """Service handling all transaction business logic."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = TransactionRepository(db)

    def _to_response(self, transaction) -> TransactionResponse:
        """Convert a Transaction model to TransactionResponse schema."""
        return TransactionResponse.from_orm_with_rel(transaction)

    def create(self, transaction: TransactionCreate) -> TransactionResponse:
        """Create a new transaction.

        Args:
            transaction: TransactionCreate schema.

        Returns:
            TransactionResponse schema.

        Raises:
            InternalError: If creation fails.
        """
        try:
            result = self.repository.create(transaction)
            self.logger.info(f"Transaction created: {result.id}")
            return self._to_response(result)
        except Exception as e:
            self.logger.error(f"Failed to create transaction: {e}")
            raise InternalError(f"Failed to create transaction: {str(e)}")

    def bulk_create(self, payload: BulkTransactionCreate):
        """Create multiple transactions atomically.

        Args:
            payload: BulkTransactionCreate schema.

        Returns:
            List of TransactionResponse schemas.
        """
        try:
            results = self.repository.bulk_create(payload.transactions)
            return [self._to_response(t) for t in results]
        except Exception as e:
            self.logger.error(f"Bulk create failed: {e}")
            raise InternalError(f"Bulk create failed: {str(e)}")

    def get_all(self):
        """Fetch all transactions."""
        return [self._to_response(t) for t in self.repository.get_all_with_category()]

    def get_by_id(self, transaction_id: int) -> TransactionResponse:
        """Fetch a transaction by id.

        Raises:
            NotFoundError: If transaction not found.
        """
        transaction = self.repository.get_by_id_with_category(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction with id {transaction_id} not found")
        return self._to_response(transaction)

    def update(self, transaction_id: int, data: TransactionCreate) -> TransactionResponse:
        """Update a transaction.

        Raises:
            NotFoundError: If transaction not found.
        """
        updated = self.repository.update(transaction_id, data)
        if not updated:
            raise NotFoundError(f"Transaction with id {transaction_id} not found")
        return self._to_response(updated)

    def delete(self, transaction_id: int):
        """Delete a transaction.

        Raises:
            NotFoundError: If transaction not found.
        """
        deleted = self.repository.delete(transaction_id)
        if not deleted:
            raise NotFoundError(f"Transaction with id {transaction_id} not found")

    def get_filtered(
        self,
        is_expense  : bool  = None,
        min_amount  : float = None,
        max_amount  : float = None,
        category_id : int   = None,
        limit       : int   = 10,
        offset      : int   = 0
    ):
        """Fetch filtered transactions."""
        results = self.repository.get_filtered(
            is_expense, min_amount, max_amount, category_id, limit, offset
        )
        return [self._to_response(t) for t in results]

    def get_summary(self) -> dict:
        """Get financial summary using native SQL."""
        return self.repository.get_summary()

    def get_category_breakdown(self) -> list:
        """Get expense breakdown by category."""
        return self.repository.get_category_breakdown()