"""AI Service - orchestrates LangChain chains and LangGraph agents."""
import logging
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from app.ai.agents.finance_agent import FinanceAgent
from app.ai.chains.finance_chains import (
    ClassifyTransactionChain,
    SummariseTransactionsChain,
    FinancialAdviceChain
)
from app.ai.llm.factory import LLMClientFactory
from app.repository.transaction_repository import TransactionRepository
from app.exceptions.app_exceptions import NotFoundError, InternalError
from app.config.langsmith_config import get_trace_metadata

logger = logging.getLogger("app.services.ai_service")


class AIService(BaseService):
    """Service handling all AI-powered operations."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.repository  = TransactionRepository(db)
        self.llm_factory = LLMClientFactory()
        self.llm_client  = self.llm_factory.get_groq_client()

    def classify_transaction(self, description: str) -> dict:
        """Classify a single transaction description."""
        self.logger.info(f"Classifying transaction: {description}")
        try:
            chain  = ClassifyTransactionChain(self.llm_client)
            result = chain.invoke({"transaction": description})
            return {
                "description"    : description,
                "classification" : result
            }
        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            raise InternalError(f"Classification failed: {str(e)}")

    def analyse_transactions(self) -> dict:
        """Run full financial analysis using the FinanceAgent."""
        self.logger.info("Running full financial analysis")

        transactions = self.repository.get_all_with_category()
        if not transactions:
            raise NotFoundError("No transactions found for analysis")

        transaction_data = [
            {
                "description": t.description,
                "amount"     : t.amount,
                "is_expense" : t.is_expense,
                "category"   : t.category_rel.name if t.category_rel else None
            }
            for t in transactions
        ]

        try:
            agent  = FinanceAgent(self.llm_client)
            result = agent.run({"transactions": transaction_data})
            self.logger.info("Full financial analysis completed")
            return result
        except Exception as e:
            self.logger.error(f"Financial analysis failed: {e}")
            raise InternalError(f"Financial analysis failed: {str(e)}")

    def get_ai_summary(self) -> dict:
        """Generate AI-powered financial summary."""
        self.logger.info("Generating AI summary")

        transactions = self.repository.get_all_with_category()
        if not transactions:
            raise NotFoundError("No transactions found for summary")

        transaction_data = [
            {
                "description": t.description,
                "amount"     : t.amount,
                "is_expense" : t.is_expense,
                "category"   : t.category_rel.name if t.category_rel else None
            }
            for t in transactions
        ]

        try:
            chain  = SummariseTransactionsChain(self.llm_client)
            result = chain.invoke({"transactions": transaction_data})
            self.logger.info("AI summary generated")
            return result
        except Exception as e:
            self.logger.error(f"AI summary failed: {e}")
            raise InternalError(f"AI summary failed: {str(e)}")

    def get_financial_advice(
        self,
        total_income   : float,
        total_expenses : float,
        savings_rate   : float,
        top_category   : str
    ) -> dict:
        """Generate personalised financial advice."""
        self.logger.info("Generating financial advice")
        try:
            chain  = FinancialAdviceChain(self.llm_client)
            result = chain.invoke({
                "total_income"   : total_income,
                "total_expenses" : total_expenses,
                "savings_rate"   : savings_rate,
                "top_category"   : top_category
            })
            return {"advice": result}
        except Exception as e:
            self.logger.error(f"Advice generation failed: {e}")
            raise InternalError(f"Advice generation failed: {str(e)}")