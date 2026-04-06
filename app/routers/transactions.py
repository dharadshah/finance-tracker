import logging
import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from groq import Groq
from dotenv import load_dotenv
from config.database_config import get_db
from app.crud import transactions as crud_transactions
from app.schemas import TransactionCreate, TransactionResponse

load_dotenv()

logger     = logging.getLogger(__name__)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    return crud_transactions.create_transaction(db, transaction)


@router.get("/analyze")
async def analyze_transactions(db: Session = Depends(get_db)):
    transactions = crud_transactions.get_transactions(db)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    transaction_data = [
        {
            "description": t.description,
            "amount"     : t.amount,
            "is_expense" : t.is_expense,
            "category"   : t.category_rel.name if t.category_rel else None
        }
        for t in transactions
    ]

    system = """
You are a financial analyst assistant for a Personal Finance Tracker API.
Always return valid JSON in this exact format with no extra text:
{
    "total_income": 0,
    "total_expenses": 0,
    "balance": 0,
    "savings_rate": 0,
    "largest_expense_category": "",
    "insight": ""
}
"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": f"Analyse these transactions: {transaction_data}"}
        ]
    )

    result = json.loads(response.choices[0].message.content)
    return result


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(db: Session = Depends(get_db)):
    return crud_transactions.get_transactions(db)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud_transactions.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction   : TransactionCreate,
    db            : Session = Depends(get_db)
):
    updated = crud_transactions.update_transaction(db, transaction_id, transaction)
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db            : Session = Depends(get_db)
):
    deleted = crud_transactions.delete_transaction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}