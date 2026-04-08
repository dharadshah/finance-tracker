import logging
import json
import os
from sqlalchemy.orm import Session
from groq import Groq
from dotenv import load_dotenv
from app.repository import transaction_repository
from app.schemas import TransactionCreate
from app.exceptions.finance_exceptions import TransactionNotFoundException
from app.prompts.finance_prompts import (
    ANALYSE_TRANSACTIONS_SYSTEM,
    SUMMARISE_TRANSACTIONS_PROMPT
)

load_dotenv()

logger      = logging.getLogger(__name__)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def create_transaction(db: Session, transaction: TransactionCreate):
    return transaction_repository.create_transaction(db, transaction)


def get_transactions(db: Session):
    return transaction_repository.get_transactions(db)


def get_transaction(db: Session, transaction_id: int):
    transaction = transaction_repository.get_transaction(db, transaction_id)
    if not transaction:
        raise TransactionNotFoundException(transaction_id)
    return transaction


def update_transaction(db: Session, transaction_id: int, data: TransactionCreate):
    updated = transaction_repository.update_transaction(db, transaction_id, data)
    if not updated:
        raise TransactionNotFoundException(transaction_id)
    return updated


def delete_transaction(db: Session, transaction_id: int):
    deleted = transaction_repository.delete_transaction(db, transaction_id)
    if not deleted:
        raise TransactionNotFoundException(transaction_id)
    return deleted


def analyse_transactions(db: Session):
    transactions = transaction_repository.get_transactions(db)
    if not transactions:
        raise TransactionNotFoundException(0)

    transaction_data = [
        {
            "description": t.description,
            "amount"     : t.amount,
            "is_expense" : t.is_expense,
            "category"   : t.category_rel.name if t.category_rel else None
        }
        for t in transactions
    ]

    response = groq_client.chat.completions.create(
        model    = "llama-3.3-70b-versatile",
        messages = [
            {"role": "system", "content": ANALYSE_TRANSACTIONS_SYSTEM},
            {"role": "user",   "content": SUMMARISE_TRANSACTIONS_PROMPT.format(
                transactions=transaction_data
            )}
        ]
    )

    return json.loads(response.choices[0].message.content)