import logging
from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import transactions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Finance Tracker",
    description="A REST API for tracking income and expenses",
    version="0.1.0"
)

app.include_router(transactions.router)


@app.get("/")
async def root():
    return {"message": "Personal Finance Tracker API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}