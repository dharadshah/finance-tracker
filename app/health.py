import logging
from fastapi import APIRouter
from app.config.settings import settings
from app.config.logging_config import logger

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    return {"message": f"{settings.app_name} is running"}


@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app_version}