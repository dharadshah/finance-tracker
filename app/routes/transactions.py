"""Transaction routes for Personal Finance Tracker API."""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.routes.base_router import BaseRouter
from app.dependencies import get_db, get_settings
from app.config.settings import Settings
from app.services.transaction_service import TransactionService
from app.schemas import TransactionCreate, TransactionResponse, BulkTransactionCreate
from app.constants.app_constants import ROUTE_CONSTANTS

logger = logging.getLogger(__name__)


class TransactionRouter(BaseRouter):
    """Router handling all transaction endpoints."""

    def __init__(self):
        super().__init__(
            prefix = ROUTE_CONSTANTS.TRANSACTIONS_PREFIX.value,
            tags   = ["Transactions"]
        )

    def register(self) -> APIRouter:
        """Register all transaction routes."""

        @self.router.post("", response_model=TransactionResponse)
        async def create_transaction(
            transaction : TransactionCreate,
            db          : Session  = Depends(get_db),
            settings    : Settings = Depends(get_settings)
        ):
            self.logger.info(f"Creating transaction: {transaction.description}")
            return TransactionService(db).create(transaction)

        @self.router.post("/bulk", response_model=List[TransactionResponse])
        async def bulk_create_transactions(
            payload  : BulkTransactionCreate,
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            self.logger.info(f"Bulk creating {len(payload.transactions)} transactions")
            return TransactionService(db).bulk_create(payload)

        @self.router.get("/summary")
        async def get_summary(
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            self.logger.info("Fetching summary")
            return TransactionService(db).get_summary()

        @self.router.get("/breakdown")
        async def get_category_breakdown(
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            self.logger.info("Fetching category breakdown")
            return TransactionService(db).get_category_breakdown()

        @self.router.get("/filter", response_model=List[TransactionResponse])
        async def get_transactions_filtered(
            is_expense  : Optional[bool]  = Query(default=None),
            min_amount  : Optional[float] = Query(default=None),
            max_amount  : Optional[float] = Query(default=None),
            category_id : Optional[int]   = Query(default=None),
            limit       : int             = Query(default=10, ge=1, le=100),
            offset      : int             = Query(default=0,  ge=0),
            db          : Session         = Depends(get_db),
            settings    : Settings        = Depends(get_settings)
        ):
            self.logger.info("Fetching filtered transactions")
            return TransactionService(db).get_filtered(
                is_expense, min_amount, max_amount, category_id, limit, offset
            )

        @self.router.get("", response_model=List[TransactionResponse])
        async def get_transactions(
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            self.logger.info("Fetching all transactions")
            return TransactionService(db).get_all()

        @self.router.get("/{transaction_id}", response_model=TransactionResponse)
        async def get_transaction(
            transaction_id : int,
            db             : Session  = Depends(get_db),
            settings       : Settings = Depends(get_settings)
        ):
            self.logger.info(f"Fetching transaction: {transaction_id}")
            return TransactionService(db).get_by_id(transaction_id)

        @self.router.put("/{transaction_id}", response_model=TransactionResponse)
        async def update_transaction(
            transaction_id : int,
            transaction    : TransactionCreate,
            db             : Session  = Depends(get_db),
            settings       : Settings = Depends(get_settings)
        ):
            self.logger.info(f"Updating transaction: {transaction_id}")
            return TransactionService(db).update(transaction_id, transaction)

        @self.router.delete("/{transaction_id}")
        async def delete_transaction(
            transaction_id : int,
            db             : Session  = Depends(get_db),
            settings       : Settings = Depends(get_settings)
        ):
            self.logger.info(f"Deleting transaction: {transaction_id}")
            TransactionService(db).delete(transaction_id)
            return {"message": "Transaction deleted successfully"}

        return self.router


# module level instance
router = TransactionRouter().register()