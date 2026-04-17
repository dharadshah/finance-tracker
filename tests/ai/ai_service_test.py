"""Tests for AIService.

Note: All LLM and chain calls are mocked - no real API calls made.
"""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.services.ai_service import AIService
from app.exceptions.app_exceptions import NotFoundError, InternalError


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_db():
    """Return a mocked database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_transaction():
    """Return a mock transaction object."""
    t              = MagicMock()
    t.description  = "Salary"
    t.amount       = 50000.0
    t.is_expense   = False
    t.category_rel = MagicMock()
    t.category_rel.name = "Income"
    return t


@pytest.fixture
def mock_expense_transaction():
    """Return a mock expense transaction."""
    t              = MagicMock()
    t.description  = "Grocery"
    t.amount       = 2500.0
    t.is_expense   = True
    t.category_rel = MagicMock()
    t.category_rel.name = "Food"
    return t


@pytest.fixture
def sample_summary():
    return {
        "total_income"             : 50000,
        "total_expenses"           : 2500,
        "balance"                  : 47500,
        "savings_rate"             : 95.0,
        "largest_expense_category" : "Food",
        "insight"                  : "You are saving well."
    }


@pytest.fixture
def ai_service(mock_db):
    """Return AIService with mocked LLM factory."""
    with patch("app.services.ai_service.LLMClientFactory") as mock_factory:
        mock_factory.return_value.get_groq_client.return_value = MagicMock()
        service = AIService(mock_db)
        service.repository = MagicMock()
        return service


# ============================================================
# AIService Initialization
# ============================================================

class TestAIServiceInit:
    """Tests for AIService initialization."""

    def test_ai_service_inherits_base_service(self, mock_db):
        """Should inherit from BaseService."""
        from app.services.base_service import BaseService
        with patch("app.services.ai_service.LLMClientFactory"):
            service = AIService(mock_db)
            assert isinstance(service, BaseService)

    def test_ai_service_stores_db(self, mock_db):
        """Should store database session."""
        with patch("app.services.ai_service.LLMClientFactory"):
            service = AIService(mock_db)
            assert service.db is mock_db

    def test_ai_service_creates_repository(self, mock_db):
        """Should create a TransactionRepository."""
        from app.repository.transaction_repository import TransactionRepository
        with patch("app.services.ai_service.LLMClientFactory"):
            service = AIService(mock_db)
            assert isinstance(service.repository, TransactionRepository)

    def test_ai_service_creates_llm_client(self, mock_db):
        """Should create an LLM client via factory."""
        with patch("app.services.ai_service.LLMClientFactory") as mock_factory:
            AIService(mock_db)
            mock_factory.return_value.get_groq_client.assert_called_once()


# ============================================================
# classify_transaction
# ============================================================

class TestClassifyTransaction:
    """Tests for AIService.classify_transaction()."""

    def test_classify_returns_dict(self, ai_service):
        """Should return a dict with classification."""
        with patch("app.services.ai_service.ClassifyTransactionChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "INCOME"
            result = ai_service.classify_transaction("Salary credited")
            assert isinstance(result, dict)

    def test_classify_returns_description(self, ai_service):
        """Should include description in result."""
        with patch("app.services.ai_service.ClassifyTransactionChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "INCOME"
            result = ai_service.classify_transaction("Salary credited")
            assert result["description"] == "Salary credited"

    def test_classify_returns_classification(self, ai_service):
        """Should include classification in result."""
        with patch("app.services.ai_service.ClassifyTransactionChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "INCOME"
            result = ai_service.classify_transaction("Salary credited")
            assert result["classification"] == "INCOME"

    def test_classify_expense_transaction(self, ai_service):
        """Should classify expense correctly."""
        with patch("app.services.ai_service.ClassifyTransactionChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "EXPENSE"
            result = ai_service.classify_transaction("Paid rent")
            assert result["classification"] == "EXPENSE"

    def test_classify_raises_internal_error_on_failure(self, ai_service):
        """Should raise InternalError when chain fails."""
        with patch("app.services.ai_service.ClassifyTransactionChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.side_effect = Exception("LLM error")
            with pytest.raises(InternalError):
                ai_service.classify_transaction("Salary")

    def test_classify_empty_description(self, ai_service):
        """Should attempt classification even with empty description."""
        with patch("app.services.ai_service.ClassifyTransactionChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "EXPENSE"
            result = ai_service.classify_transaction("")
            assert "classification" in result


# ============================================================
# analyse_transactions
# ============================================================

class TestAnalyseTransactions:
    """Tests for AIService.analyse_transactions()."""

    def test_analyse_raises_not_found_when_no_transactions(self, ai_service):
        """Should raise NotFoundError when no transactions exist."""
        ai_service.repository.get_all_with_category.return_value = []
        with pytest.raises(NotFoundError):
            ai_service.analyse_transactions()

    def test_analyse_returns_dict(
        self, ai_service, mock_transaction, sample_summary
    ):
        """Should return a dict report."""
        ai_service.repository.get_all_with_category.return_value = [mock_transaction]
        with patch("app.services.ai_service.FinanceAgent") as mock_agent_cls:
            mock_agent_cls.return_value.run.return_value = {
                "transactions"  : [],
                "summary"       : sample_summary,
                "advice"        : "Save more.",
                "has_high_risk" : False,
                "error"         : None
            }
            result = ai_service.analyse_transactions()
            assert isinstance(result, dict)

    def test_analyse_report_contains_summary(
        self, ai_service, mock_transaction, sample_summary
    ):
        """Should return report with summary."""
        ai_service.repository.get_all_with_category.return_value = [mock_transaction]
        with patch("app.services.ai_service.FinanceAgent") as mock_agent_cls:
            mock_agent_cls.return_value.run.return_value = {
                "transactions"  : [],
                "summary"       : sample_summary,
                "advice"        : "Save more.",
                "has_high_risk" : False,
                "error"         : None
            }
            result = ai_service.analyse_transactions()
            assert "summary" in result

    def test_analyse_raises_internal_error_on_agent_failure(
        self, ai_service, mock_transaction
    ):
        """Should raise InternalError when agent fails."""
        ai_service.repository.get_all_with_category.return_value = [mock_transaction]
        with patch("app.services.ai_service.FinanceAgent") as mock_agent_cls:
            mock_agent_cls.return_value.run.side_effect = Exception("Agent error")
            with pytest.raises(InternalError):
                ai_service.analyse_transactions()

    def test_analyse_passes_correct_transaction_data_to_agent(
        self, ai_service, mock_transaction, sample_summary
    ):
        """Should pass formatted transaction data to agent."""
        ai_service.repository.get_all_with_category.return_value = [mock_transaction]
        with patch("app.services.ai_service.FinanceAgent") as mock_agent_cls:
            mock_agent_cls.return_value.run.return_value = {
                "transactions": [], "summary": sample_summary,
                "advice": "", "has_high_risk": False, "error": None
            }
            ai_service.analyse_transactions()
            call_args = mock_agent_cls.return_value.run.call_args[0][0]
            transactions = call_args["transactions"]
            assert len(transactions) == 1
            assert transactions[0]["description"] == "Salary"
            assert transactions[0]["amount"]      == 50000.0

    def test_analyse_handles_transaction_without_category(
        self, ai_service, sample_summary
    ):
        """Should handle transactions with no category."""
        t              = MagicMock()
        t.description  = "Cash"
        t.amount       = 1000.0
        t.is_expense   = True
        t.category_rel = None

        ai_service.repository.get_all_with_category.return_value = [t]
        with patch("app.services.ai_service.FinanceAgent") as mock_agent_cls:
            mock_agent_cls.return_value.run.return_value = {
                "transactions": [], "summary": sample_summary,
                "advice": "", "has_high_risk": False, "error": None
            }
            result = ai_service.analyse_transactions()
            assert isinstance(result, dict)


# ============================================================
# get_ai_summary
# ============================================================

class TestGetAISummary:
    """Tests for AIService.get_ai_summary()."""

    def test_summary_raises_not_found_when_no_transactions(self, ai_service):
        """Should raise NotFoundError when no transactions exist."""
        ai_service.repository.get_all_with_category.return_value = []
        with pytest.raises(NotFoundError):
            ai_service.get_ai_summary()

    def test_summary_returns_dict(self, ai_service, mock_transaction, sample_summary):
        """Should return summary dict."""
        ai_service.repository.get_all_with_category.return_value = [mock_transaction]
        with patch("app.services.ai_service.SummariseTransactionsChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = sample_summary
            result = ai_service.get_ai_summary()
            assert isinstance(result, dict)

    def test_summary_contains_expected_keys(
        self, ai_service, mock_transaction, sample_summary
    ):
        """Summary should contain all expected keys."""
        ai_service.repository.get_all_with_category.return_value = [mock_transaction]
        with patch("app.services.ai_service.SummariseTransactionsChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = sample_summary
            result = ai_service.get_ai_summary()
            assert "total_income"   in result
            assert "total_expenses" in result
            assert "balance"        in result
            assert "savings_rate"   in result

    def test_summary_raises_internal_error_on_chain_failure(
        self, ai_service, mock_transaction
    ):
        """Should raise InternalError when chain fails."""
        ai_service.repository.get_all_with_category.return_value = [mock_transaction]
        with patch("app.services.ai_service.SummariseTransactionsChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.side_effect = Exception("Chain error")
            with pytest.raises(InternalError):
                ai_service.get_ai_summary()


# ============================================================
# get_financial_advice
# ============================================================

class TestGetFinancialAdvice:
    """Tests for AIService.get_financial_advice()."""

    def test_advice_returns_dict(self, ai_service):
        """Should return dict with advice key."""
        with patch("app.services.ai_service.FinancialAdviceChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "Save more."
            result = ai_service.get_financial_advice(
                total_income   = 50000,
                total_expenses = 10000,
                savings_rate   = 80,
                top_category   = "Housing"
            )
            assert isinstance(result, dict)
            assert "advice" in result

    def test_advice_contains_advice_string(self, ai_service):
        """Advice value should be a non-empty string."""
        with patch("app.services.ai_service.FinancialAdviceChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "Save more."
            result = ai_service.get_financial_advice(
                total_income   = 50000,
                total_expenses = 10000,
                savings_rate   = 80,
                top_category   = "Housing"
            )
            assert isinstance(result["advice"], str)
            assert len(result["advice"]) > 0

    def test_advice_passes_correct_values_to_chain(self, ai_service):
        """Should pass correct values to advice chain."""
        with patch("app.services.ai_service.FinancialAdviceChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "Save more."
            ai_service.get_financial_advice(
                total_income   = 50000,
                total_expenses = 10000,
                savings_rate   = 80,
                top_category   = "Housing"
            )
            call_args = mock_chain_cls.return_value.invoke.call_args[0][0]
            assert call_args["total_income"]   == 50000
            assert call_args["total_expenses"] == 10000
            assert call_args["savings_rate"]   == 80
            assert call_args["top_category"]   == "Housing"

    def test_advice_raises_internal_error_on_failure(self, ai_service):
        """Should raise InternalError when chain fails."""
        with patch("app.services.ai_service.FinancialAdviceChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.side_effect = Exception("LLM error")
            with pytest.raises(InternalError):
                ai_service.get_financial_advice(
                    total_income   = 50000,
                    total_expenses = 10000,
                    savings_rate   = 80,
                    top_category   = "Housing"
                )

    def test_advice_with_zero_values(self, ai_service):
        """Should handle zero income and expenses."""
        with patch("app.services.ai_service.FinancialAdviceChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "Start saving."
            result = ai_service.get_financial_advice(
                total_income   = 0,
                total_expenses = 0,
                savings_rate   = 0,
                top_category   = "None"
            )
            assert "advice" in result

    def test_advice_with_high_savings_rate(self, ai_service):
        """Should handle high savings rate."""
        with patch("app.services.ai_service.FinancialAdviceChain") as mock_chain_cls:
            mock_chain_cls.return_value.invoke.return_value = "Excellent savings!"
            result = ai_service.get_financial_advice(
                total_income   = 100000,
                total_expenses = 5000,
                savings_rate   = 95,
                top_category   = "Food"
            )
            assert result["advice"] == "Excellent savings!"