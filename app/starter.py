from app.config.logging_config import logger
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings
from app.config.logging_config import setup_logging
from app.config.database_config import engine, SessionLocal, Base
from app.routes.categories import router as categories_router
from app.routes.transactions import router as transactions_router
from app.routes.ai_routes import router as ai_router
from app import health
from app.services.category_service import CategoryService
from app.exceptions.handlers import register_exception_handlers

setup_logging()



class VersionHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-API-Version"] = settings.app_version
        return response


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        CategoryService(db).seed_defaults()
    finally:
        db.close()

    app = FastAPI(
        title   = settings.app_name,
        version = settings.app_version
    )

    register_exception_handlers(app)
    app.add_middleware(VersionHeaderMiddleware)

    app.include_router(health.router)
    app.include_router(transactions_router)
    app.include_router(categories_router)
    app.include_router(ai_router)

    logger.info(f"{settings.app_name} started successfully")

    return app