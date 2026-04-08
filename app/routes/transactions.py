import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_settings
from app.config.settings import Settings
from app.services import transaction_service
from app.schemas import TransactionCreate, TransactionResponse
from app.constants.app_constants import ROUTE_CONSTANTS

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = ROUTE_CONSTANTS.TRANSACTIONS_PREFIX.value,
    tags   = ["Transactions"]
)


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction : TransactionCreate,
    db          : Session  = Depends(get_db),
    settings    : Settings = Depends(get_settings)
):
    return transaction_service.create_transaction(db, transaction)


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(
    db       : Session  = Depends(get_db),
    settings : Settings = Depends(get_settings)
):
    return transaction_service.get_transactions(db)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id : int,
    db             : Session  = Depends(get_db),
    settings       : Settings = Depends(get_settings)
):
    return transaction_service.get_transaction(db, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id : int,
    transaction    : TransactionCreate,
    db             : Session  = Depends(get_db),
    settings       : Settings = Depends(get_settings)
):
    return transaction_service.update_transaction(db, transaction_id, transaction)


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id : int,
    db             : Session  = Depends(get_db),
    settings       : Settings = Depends(get_settings)
):
    transaction_service.delete_transaction(db, transaction_id)
    return {"message": "Transaction deleted successfully"}