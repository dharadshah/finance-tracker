import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud
from app.schemas import TransactionCreate, TransactionResponse

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.get("/analyze")
async def analyze_transactions(db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db)

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    transaction_data = [
        {
            "description": t.description,
            "amount":      t.amount,
            "is_expense":  t.is_expense,
            "category":    t.category
        }
        for t in transactions
    ]

    system = """
You are a financial analyst assistant for a Personal Finance
Tracker API. Analyse transaction data and provide actionable insights.
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

    import json
    result = json.loads(response.choices[0].message.content)
    return result


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    return crud.create_transaction(db, transaction)


@router.get("", response_model=List[TransactionResponse])
async def get_transactions(db: Session = Depends(get_db)):
    return crud.get_transactions(db)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    updated = crud.update_transaction(db, transaction_id, transaction)
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    deleted = crud.delete_transaction(db, transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}


