"""Tests for Finance Tracker LangChain chains.

Note: All LLM calls are mocked - no real API calls made.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from langchain_core.messages import AIMessage
from app.ai.chains.base_chain import BaseChain
from app.ai.chains.finance_chains import (
    ClassifyTransactionChain,
    AnalyseTransactionChain,
    SummariseTransactionsChain,
    FinancialAdviceChain
)
from app.ai.llm.base_client import LLMConfig
from app.ai.llm.groq_client import GroqLLMClient


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_llm_client():
    """Return a mocked LLM client."""
    client        = MagicMock(spec=GroqLLMClient)
    client.config = LLMConfig(model_name="test-model")
    return client

def _mock_chain_invoke(chain_instance, response_text: str):
    """Helper to mock the built chain's invoke method."""
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = response_text
    chain_instance.build = MagicMock(return_value=mock_chain)
    return mock_chain

@pytest.fixture
def mock_model_response():
    """Helper to set mock model response."""
    def _set_response(mock_client, response_text: str):
        mock_model = mock_client.get_model.return_value
        mock_model.invoke.return_value = AIMessage(content=response_text)
        return mock_model
    return _set_response


@pytest.fixture
def classify_chain(mock_llm_client):
    return ClassifyTransactionChain(mock_llm_client)


@pytest.fixture
def analyse_chain(mock_llm_client):
    return AnalyseTransactionChain(mock_llm_client)


@pytest.fixture
def summarise_chain(mock_llm_client):
    return SummariseTransactionsChain(mock_llm_client)


@pytest.fixture
def advice_chain(mock_llm_client):
    return FinancialAdviceChain(mock_llm_client)


@pytest.fixture
def sample_transactions():
    return [
        {"description": "Salary",  "amount": 50000, "is_expense": False},
        {"description": "Grocery", "amount": 2500,  "is_expense": True},
        {"description": "Netflix", "amount": 649,   "is_expense": True}
    ]


# ============================================================
# BaseChain
# ============================================================

class TestBaseChain:
    """Tests for BaseChain via concrete subclass."""

    def test_repr_contains_class_name(self, classify_chain):
        """Repr should contain class name."""
        assert "ClassifyTransactionChain" in repr(classify_chain)

    def test_repr_contains_model_name(self, classify_chain):
        """Repr should contain model name."""
        assert "test-model" in repr(classify_chain)

    def test_stores_llm_client(self, classify_chain, mock_llm_client):
        """Should store llm_client reference."""
        assert classify_chain.llm_client is mock_llm_client

    def test_build_returns_runnable(self, classify_chain):
        """Build should return a Runnable."""
        from langchain_core.runnables import Runnable
        chain = classify_chain.build()
        assert chain is not None


# ============================================================
# ClassifyTransactionChain
# ============================================================

class TestClassifyTransactionChain:
    """Tests for ClassifyTransactionChain."""

    def test_prompt_is_correct_type(self, classify_chain):
        """Should use ClassifyTransactionPrompt."""
        from app.prompts.finance_prompts import ClassifyTransactionPrompt
        assert isinstance(classify_chain.prompt, ClassifyTransactionPrompt)

    def test_invoke_returns_income(self, classify_chain):
        """Should return INCOME for income transaction."""
        _mock_chain_invoke(classify_chain, "INCOME")
        result = classify_chain.invoke({"transaction": "Salary credited"})
        assert result == "INCOME"

    def test_invoke_returns_expense(self, classify_chain):
        """Should return EXPENSE for expense transaction."""
        _mock_chain_invoke(classify_chain, "EXPENSE")
        result = classify_chain.invoke({"transaction": "Paid rent"})
        assert result == "EXPENSE"

    def test_invoke_sanitizes_lowercase_income(self, classify_chain):
        """Should handle lowercase income response."""
        _mock_chain_invoke(classify_chain, "income")
        result = classify_chain.invoke({"transaction": "Salary"})
        assert result == "INCOME"

    def test_invoke_sanitizes_verbose_response(self, classify_chain):
        """Should extract INCOME from verbose response."""
        _mock_chain_invoke(classify_chain, "This is an INCOME transaction.")
        result = classify_chain.invoke({"transaction": "Salary"})
        assert result == "INCOME"

    def test_invoke_defaults_to_expense_for_unknown(self, classify_chain):
        """Should default to EXPENSE for unrecognized response."""
        _mock_chain_invoke(classify_chain, "unknown response")
        result = classify_chain.invoke({"transaction": "Something"})
        assert result == "EXPENSE"

    def test_invoke_result_is_string(self, classify_chain):
        """Result should always be a string."""
        _mock_chain_invoke(classify_chain, "INCOME")
        result = classify_chain.invoke({"transaction": "Salary"})
        assert isinstance(result, str)


# ============================================================
# AnalyseTransactionChain
# ============================================================

class TestAnalyseTransactionChain:

    def test_prompt_is_correct_type(self, analyse_chain):
        from app.prompts.finance_prompts import AnalyseTransactionPrompt
        assert isinstance(analyse_chain.prompt, AnalyseTransactionPrompt)

    def test_invoke_returns_dict(self, analyse_chain):
        _mock_chain_invoke(analyse_chain, '{"category": "Food", "risk_level": "Low"}')
        result = analyse_chain.invoke({
            "description"    : "Grocery",
            "amount"         : 2500,
            "classification" : "EXPENSE"
        })
        assert isinstance(result, dict)
        assert result["category"]   == "Food"
        assert result["risk_level"] == "Low"

    def test_invoke_handles_json_with_code_block(self, analyse_chain):
        _mock_chain_invoke(analyse_chain, '```json\n{"category": "Food", "risk_level": "Low"}\n```')
        result = analyse_chain.invoke({
            "description"    : "Grocery",
            "amount"         : 2500,
            "classification" : "EXPENSE"
        })
        assert result["category"] == "Food"

    def test_invoke_raises_error_on_invalid_json(self, analyse_chain):
        _mock_chain_invoke(analyse_chain, "not valid json")
        with pytest.raises(Exception):
            analyse_chain.invoke({
                "description"    : "Grocery",
                "amount"         : 2500,
                "classification" : "EXPENSE"
            })

    def test_invoke_with_income_transaction(self, analyse_chain):
        _mock_chain_invoke(analyse_chain, '{"category": "Income", "risk_level": "Low"}')
        result = analyse_chain.invoke({
            "description"    : "Salary",
            "amount"         : 50000,
            "classification" : "INCOME"
        })
        assert result["category"] == "Income"


# ============================================================
# SummariseTransactionsChain
# ============================================================

class TestSummariseTransactionsChain:

    @pytest.fixture
    def valid_summary_response(self):
        return """{
            "total_income"             : 50000,
            "total_expenses"           : 3149,
            "balance"                  : 46851,
            "savings_rate"             : 93.7,
            "largest_expense_category" : "Food",
            "insight"                  : "You are saving well."
        }"""

    def test_prompt_is_correct_type(self, summarise_chain):
        from app.prompts.finance_prompts import SummariseTransactionsPrompt
        assert isinstance(summarise_chain.prompt, SummariseTransactionsPrompt)

    def test_invoke_returns_dict(self, summarise_chain, valid_summary_response, sample_transactions):
        _mock_chain_invoke(summarise_chain, valid_summary_response)
        result = summarise_chain.invoke({"transactions": sample_transactions})
        assert isinstance(result, dict)

    def test_invoke_contains_all_keys(self, summarise_chain, valid_summary_response, sample_transactions):
        _mock_chain_invoke(summarise_chain, valid_summary_response)
        result = summarise_chain.invoke({"transactions": sample_transactions})
        assert "total_income"             in result
        assert "total_expenses"           in result
        assert "balance"                  in result
        assert "savings_rate"             in result
        assert "largest_expense_category" in result
        assert "insight"                  in result

    def test_invoke_handles_code_block_response(self, summarise_chain, valid_summary_response, sample_transactions):
        _mock_chain_invoke(summarise_chain, f"```json\n{valid_summary_response}\n```")
        result = summarise_chain.invoke({"transactions": sample_transactions})
        assert result["total_income"] == 50000

    def test_invoke_raises_error_on_invalid_json(self, summarise_chain, sample_transactions):
        _mock_chain_invoke(summarise_chain, "not valid json")
        with pytest.raises(Exception):
            summarise_chain.invoke({"transactions": sample_transactions})


# ============================================================
# FinancialAdviceChain
# ============================================================

class TestFinancialAdviceChain:

    def test_prompt_is_correct_type(self, advice_chain):
        from app.prompts.finance_prompts import FinancialAdvicePrompt
        assert isinstance(advice_chain.prompt, FinancialAdvicePrompt)

    def test_invoke_returns_string(self, advice_chain):
        _mock_chain_invoke(advice_chain, "Consider saving more each month.")
        result = advice_chain.invoke({
            "total_income"   : 50000,
            "total_expenses" : 10000,
            "savings_rate"   : 80,
            "top_category"   : "Housing"
        })
        assert isinstance(result, str)

    def test_invoke_strips_whitespace(self, advice_chain):
        _mock_chain_invoke(advice_chain, "  Consider saving more.  ")
        result = advice_chain.invoke({
            "total_income"   : 50000,
            "total_expenses" : 10000,
            "savings_rate"   : 80,
            "top_category"   : "Housing"
        })
        assert result == "Consider saving more."

    def test_invoke_returns_nonempty_string(self, advice_chain):
        _mock_chain_invoke(advice_chain, "Save more money.")
        result = advice_chain.invoke({
            "total_income"   : 50000,
            "total_expenses" : 10000,
            "savings_rate"   : 80,
            "top_category"   : "Food"
        })
        assert len(result) > 0