import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from logging import Logger
from typing import List, Optional
from app.dependencies import get_db, get_settings, get_logger
from app.config.settings import Settings
from app.services import transaction_service
from app.schemas import TransactionCreate, TransactionResponse, BulkTransactionCreate
from app.constants.app_constants import ROUTE_CONSTANTS

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = ROUTE_CONSTANTS.TRANSACTIONS_PREFIX.value,
    tags   = ["Transactions"]
)


def get_transaction_logger() -> Logger:
    return get_logger("app.routes.transactions")


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction : TransactionCreate,
    db          : Session  = Depends(get_db),
    settings    : Settings = Depends(get_settings),
    logger      : Logger   = Depends(get_transaction_logger)
):
    logger.info(f"Creating transaction: {transaction.description}")
    return transaction_service.create_transaction(db, transaction)


@router.post("/bulk", response_model=List[TransactionResponse])
async def bulk_create_transactions(
    payload  : BulkTransactionCreate,
    db       : Session  = Depends(get_db),
    settings : Settings = Depends(get_settings),
    logger   : Logger   = Depends(get_transaction_logger)
):
    logger.info(f"Bulk creating {len(payload.transactions)} transactions")
    return transaction_service.bulk_create_transactions(db, payload.transactions)


@router.get("/summary")
async def get_summary(
    db       : Session  = Depends(get_db),
    settings : Settings = Depends(get_settings),
    logger   : Logger   = Depends(get_transaction_logger)
):
    logger.info("Fetching transaction summary")
    return transaction_service.get_summary(db)


@router.get("/breakdown")
async def get_category_breakdown(
    db       : Session  = Depends(get_db),
    settings : Settings = Depends(get_settings),
    logger   : Logger   = Depends(get_transaction_logger)
):
    logger.info("Fetching category breakdown")
    return transaction_service.get_category_breakdown(db)


@router.get("/filter", response_model=List[TransactionResponse])
async def get_transactions_filtered(
    is_expense  : Optional[bool]  = Query(default=None),
    min_amount  : Optional[float] = Query(default=None),
    max_amount  : Optional[float] = Query(default=None),
    category_id : Optional[int]   = Query(default=None),
    db          : Session         = Depends(get_db),
    settings    : Settings        = Depends(get_settings),
    logger      : Logger          = Depends(get_transaction_logger)
):
    logger.info("Fetching filtered transactions")
    return transaction_service.get_transactions_filtered(
        db, is_expense, min_amount, max_amount, category_id
    )


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
    db       : Session  = Depends(get_db),
    settings : Settings = Depends(get_settings),
    logger   : Logger   = Depends(get_transaction_logger)
):
    return transaction_service.get_transactions(db)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id : int,
    db             : Session  = Depends(get_db),
    settings       : Settings = Depends(get_settings),
    logger         : Logger   = Depends(get_transaction_logger)
):
    logger.info(f"Fetching transaction: {transaction_id}")
    return transaction_service.get_transaction(db, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id : int,
    transaction    : TransactionCreate,
    db             : Session  = Depends(get_db),
    settings       : Settings = Depends(get_settings),
    logger         : Logger   = Depends(get_transaction_logger)
):
    logger.info(f"Updating transaction: {transaction_id}")
    return transaction_service.update_transaction(db, transaction_id, transaction)


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id : int,
    db             : Session  = Depends(get_db),
    settings       : Settings = Depends(get_settings),
    logger         : Logger   = Depends(get_transaction_logger)
):
    logger.info(f"Deleting transaction: {transaction_id}")
    transaction_service.delete_transaction(db, transaction_id)
    return {"message": "Transaction deleted successfully"}