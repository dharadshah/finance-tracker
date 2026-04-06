import logging
from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import transactions
from app.config import settings
from config.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

app.include_router(transactions.router)


@app.get("/")
async def root():
    return {"message": f"{settings.app_name} is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}