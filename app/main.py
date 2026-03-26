import logging
from fastapi import FastAPI
from app.database import engine
from app import models
from app.schemas import TransactionCreate, TransactionResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# creates all tables defined in models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Finance Tracker",
    description="A REST API for tracking income and expenses",
    version="0.1.0"
)


@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Personal Finance Tracker API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate):
    logger.info(f"Creating transaction: {transaction.description}")
    return {
        "id": 1,
        "description": transaction.description,
        "amount": transaction.amount,
        "is_expense": transaction.is_expense,
        "category": transaction.category
    }