"""AI routes for Personal Finance Tracker API."""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.routes.base_router import BaseRouter
from app.dependencies import get_db, get_settings
from app.config.settings import Settings
from app.services.ai_service import AIService
from app.schemas.ai_schema import (
    ClassifyRequest,
    ClassifyResponse,
    AdviceRequest,
    AdviceResponse,
    AnalysisReport,
    RAGQueryRequest,
    RAGQueryResponse    
)
from app.constants.app_constants import ROUTE_CONSTANTS

logger = logging.getLogger("app.routes.ai_routes")


class AIRouter(BaseRouter):
    """Router handling all AI-powered endpoints."""

    def __init__(self):
        super().__init__(
            prefix = ROUTE_CONSTANTS.AI_PREFIX.value,
            tags   = ["AI"]
        )

    def register(self) -> APIRouter:
        """Register all AI routes."""

        @self.router.post("/classify", response_model=ClassifyResponse)
        async def classify_transaction(
            request  : ClassifyRequest,
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            """Classify a transaction description as INCOME or EXPENSE."""
            self.logger.info(f"Classifying: {request.description}")
            return AIService(db).classify_transaction(request.description)

        @self.router.get("/analyse", response_model=AnalysisReport)
        async def analyse_transactions(
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            """Run full LangGraph agent analysis on all transactions."""
            self.logger.info("Running full financial analysis")
            return AIService(db).analyse_transactions()

        @self.router.get("/summary")
        async def get_ai_summary(
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            """Generate AI-powered financial summary."""
            self.logger.info("Generating AI summary")
            return AIService(db).get_ai_summary()

        @self.router.post("/advice", response_model=AdviceResponse)
        async def get_financial_advice(
            request  : AdviceRequest,
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            """Generate personalised financial advice."""
            self.logger.info("Generating financial advice")
            return AIService(db).get_financial_advice(
                total_income   = request.total_income,
                total_expenses = request.total_expenses,
                savings_rate   = request.savings_rate,
                top_category   = request.top_category
            )

        @self.router.post("/query", response_model=RAGQueryResponse)
        async def query_finances(
            request  : RAGQueryRequest,
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            """Answer natural language questions about your finances using RAG."""
            self.logger.info(f"RAG query: {request.question}")
            return AIService(db).query_finances(request.question)

        return self.router


# module level instance
router = AIRouter().register()