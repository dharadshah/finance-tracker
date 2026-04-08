import logging
import json
import os
from sqlalchemy.orm import Session
from groq import Groq
from dotenv import load_dotenv
from app.repository import transaction_repository
from app.schemas import TransactionCreate
from app.schemas.transaction_schema import TransactionResponse
from app.exceptions.finance_exceptions import TransactionNotFoundException
from app.prompts.finance_prompts import (
    ANALYSE_TRANSACTIONS_SYSTEM,
    SUMMARISE_TRANSACTIONS_PROMPT
)

load_dotenv()

logger      = logging.getLogger(__name__)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def create_transaction(db: Session, transaction: TransactionCreate):
    result = transaction_repository.create_transaction(db, transaction)
    return TransactionResponse.from_orm_with_rel(result)


def get_transaction(db: Session, transaction_id: int):
    transaction = transaction_repository.get_transaction(db, transaction_id)
    if not transaction:
        raise TransactionNotFoundException(transaction_id)
    return TransactionResponse.from_orm_with_rel(transaction)


def get_transactions(db: Session):
    transactions = transaction_repository.get_transactions(db)
    return [TransactionResponse.from_orm_with_rel(t) for t in transactions]


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

from app.exceptions.finance_exceptions import (
    TransactionNotFoundException,
    AIAnalysisException
)

def analyse_transactions(db: Session):
    transactions = transaction_repository.get_transactions(db)
    if not transactions:
        raise TransactionNotFoundException(0)

    try:
        transaction_data = [...]
        response = groq_client.chat.completions.create(...)
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise AIAnalysisException(f"AI analysis failed: {str(e)}")