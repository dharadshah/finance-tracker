"""Tests for Finance Tracker LangGraph agents.

Note: All chain calls are mocked - no real API calls made.
"""
import pytest
from unittest.mock import MagicMock, patch
from app.ai.agents.finance_agent import FinanceAgent, FinanceAgentState
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


@pytest.fixture
def finance_agent(mock_llm_client):
    """Return a FinanceAgent with mocked chains."""
    agent = FinanceAgent(mock_llm_client)
    agent.classify_chain  = MagicMock()
    agent.analyse_chain   = MagicMock()
    agent.summarise_chain = MagicMock()
    agent.advice_chain    = MagicMock()
    return agent


@pytest.fixture
def sample_transactions():
    return [
        {"description": "Salary",   "amount": 50000, "is_expense": False},
        {"description": "Grocery",  "amount": 2500,  "is_expense": True},
        {"description": "Netflix",  "amount": 649,   "is_expense": True}
    ]


@pytest.fixture
def sample_summary():
    return {
        "total_income"             : 50000,
        "total_expenses"           : 3149,
        "balance"                  : 46851,
        "savings_rate"             : 93.7,
        "largest_expense_category" : "Food",
        "insight"                  : "You are saving well."
    }


def setup_agent_mocks(agent, summary: dict, classification="INCOME"):
    """Helper to set up all chain mocks for the agent."""
    agent.classify_chain.invoke.return_value  = classification
    agent.analyse_chain.invoke.return_value   = {
        "category"  : "Food",
        "risk_level": "Low"
    }
    agent.summarise_chain.invoke.return_value = summary
    agent.advice_chain.invoke.return_value    = "Consider saving more."


# ============================================================
# FinanceAgentState
# ============================================================

class TestFinanceAgentState:
    """Tests for FinanceAgentState TypedDict."""

    def test_state_can_be_created(self, sample_transactions):
        """Should create state with all required fields."""
        state = FinanceAgentState(
            transactions  = sample_transactions,
            classified    = [],
            analysed      = [],
            summary       = None,
            advice        = None,
            has_high_risk = False,
            error         = None,
            report        = None
        )
        assert state["transactions"] == sample_transactions
        assert state["classified"]   == []
        assert state["error"]        is None

    def test_state_has_all_required_keys(self, sample_transactions):
        """State should contain all required keys."""
        state = FinanceAgentState(
            transactions  = sample_transactions,
            classified    = [],
            analysed      = [],
            summary       = None,
            advice        = None,
            has_high_risk = False,
            error         = None,
            report        = None
        )
        assert "transactions"  in state
        assert "classified"    in state
        assert "analysed"      in state
        assert "summary"       in state
        assert "advice"        in state
        assert "has_high_risk" in state
        assert "error"         in state
        assert "report"        in state


# ============================================================
# FinanceAgent — Initialization
# ============================================================

class TestFinanceAgentInit:
    """Tests for FinanceAgent initialization."""

    def test_agent_initializes_all_chains(self, mock_llm_client):
        """Should initialize all four chains."""
        from app.ai.chains.finance_chains import (
            ClassifyTransactionChain,
            AnalyseTransactionChain,
            SummariseTransactionsChain,
            FinancialAdviceChain
        )
        agent = FinanceAgent(mock_llm_client)
        assert isinstance(agent.classify_chain,  ClassifyTransactionChain)
        assert isinstance(agent.analyse_chain,   AnalyseTransactionChain)
        assert isinstance(agent.summarise_chain, SummariseTransactionsChain)
        assert isinstance(agent.advice_chain,    FinancialAdviceChain)

    def test_repr_contains_class_name(self, mock_llm_client):
        """Repr should contain class name."""
        agent = FinanceAgent(mock_llm_client)
        assert "FinanceAgent" in repr(agent)

    def test_graph_is_none_before_first_run(self, mock_llm_client):
        """Graph should be lazily initialized."""
        agent = FinanceAgent(mock_llm_client)
        assert agent._graph is None


# ============================================================
# FinanceAgent — Individual Nodes
# ============================================================

class TestValidateNode:
    """Tests for FinanceAgent.validate_node()."""

    def test_validate_with_transactions_returns_no_error(
        self, finance_agent, sample_transactions
    ):
        """Should return no error when transactions exist."""
        state  = FinanceAgentState(
            transactions=sample_transactions, classified=[],
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.validate_node(state)
        assert result["error"] is None

    def test_validate_with_empty_transactions_returns_error(self, finance_agent):
        """Should return error when transactions list is empty."""
        state  = FinanceAgentState(
            transactions=[], classified=[],
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.validate_node(state)
        assert result["error"] is not None
        assert len(result["error"]) > 0

    def test_validate_error_message_is_descriptive(self, finance_agent):
        """Error message should describe the problem."""
        state  = FinanceAgentState(
            transactions=[], classified=[],
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.validate_node(state)
        assert "transaction" in result["error"].lower()


class TestClassifyNode:
    """Tests for FinanceAgent.classify_node()."""

    def test_classify_adds_classification_to_each_transaction(
        self, finance_agent, sample_transactions
    ):
        """Should add classification field to each transaction."""
        finance_agent.classify_chain.invoke.return_value = "INCOME"
        state  = FinanceAgentState(
            transactions=sample_transactions, classified=[],
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.classify_node(state)
        assert len(result["classified"]) == len(sample_transactions)
        for t in result["classified"]:
            assert "classification" in t

    def test_classify_calls_chain_for_each_transaction(
        self, finance_agent, sample_transactions
    ):
        """Should call classify chain once per transaction."""
        finance_agent.classify_chain.invoke.return_value = "EXPENSE"
        state  = FinanceAgentState(
            transactions=sample_transactions, classified=[],
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        finance_agent.classify_node(state)
        assert finance_agent.classify_chain.invoke.call_count == len(sample_transactions)

    def test_classify_preserves_original_fields(
        self, finance_agent, sample_transactions
    ):
        """Should preserve all original transaction fields."""
        finance_agent.classify_chain.invoke.return_value = "INCOME"
        state  = FinanceAgentState(
            transactions=sample_transactions, classified=[],
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.classify_node(state)
        for original, classified in zip(sample_transactions, result["classified"]):
            assert classified["description"] == original["description"]
            assert classified["amount"]      == original["amount"]


class TestAnalyseNode:
    """Tests for FinanceAgent.analyse_node()."""

    @pytest.fixture
    def classified_transactions(self, sample_transactions):
        return [
            {**t, "classification": "EXPENSE" if t["is_expense"] else "INCOME"}
            for t in sample_transactions
        ]

    def test_analyse_adds_category_and_risk(
        self, finance_agent, classified_transactions
    ):
        """Should add category and risk_level to each transaction."""
        finance_agent.analyse_chain.invoke.return_value = {
            "category": "Food", "risk_level": "Low"
        }
        state  = FinanceAgentState(
            transactions=[], classified=classified_transactions,
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.analyse_node(state)
        for t in result["analysed"]:
            assert "category"   in t
            assert "risk_level" in t

    def test_analyse_detects_high_risk(
        self, finance_agent, classified_transactions
    ):
        """Should set has_high_risk True when any transaction is High risk."""
        finance_agent.analyse_chain.invoke.return_value = {
            "category": "Other", "risk_level": "High"
        }
        state  = FinanceAgentState(
            transactions=[], classified=classified_transactions,
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.analyse_node(state)
        assert result["has_high_risk"] is True

    def test_analyse_no_high_risk_flag_for_low_risk(
        self, finance_agent, classified_transactions
    ):
        """Should keep has_high_risk False for low risk transactions."""
        finance_agent.analyse_chain.invoke.return_value = {
            "category": "Food", "risk_level": "Low"
        }
        state  = FinanceAgentState(
            transactions=[], classified=classified_transactions,
            analysed=[], summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.analyse_node(state)
        assert result["has_high_risk"] is False


class TestSummariseNode:
    """Tests for FinanceAgent.summarise_node()."""

    def test_summarise_returns_summary_dict(
        self, finance_agent, sample_summary
    ):
        """Should return summary dict from chain."""
        finance_agent.summarise_chain.invoke.return_value = sample_summary
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[{"description": "Test"}],
            summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.summarise_node(state)
        assert result["summary"] == sample_summary

    def test_summarise_calls_chain_once(self, finance_agent, sample_summary):
        """Should call summarise chain exactly once."""
        finance_agent.summarise_chain.invoke.return_value = sample_summary
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        finance_agent.summarise_node(state)
        finance_agent.summarise_chain.invoke.assert_called_once()


class TestAdviceNode:
    """Tests for FinanceAgent.advice_node()."""

    def test_advice_returns_string(self, finance_agent, sample_summary):
        """Should return advice string."""
        finance_agent.advice_chain.invoke.return_value = "Save more."
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=sample_summary, advice=None,
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.advice_node(state)
        assert result["advice"] == "Save more."

    def test_advice_uses_summary_values(self, finance_agent, sample_summary):
        """Should pass summary values to advice chain."""
        finance_agent.advice_chain.invoke.return_value = "Save more."
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=sample_summary, advice=None,
            has_high_risk=False, error=None, report=None
        )
        finance_agent.advice_node(state)
        call_args = finance_agent.advice_chain.invoke.call_args[0][0]
        assert call_args["total_income"]   == sample_summary["total_income"]
        assert call_args["total_expenses"] == sample_summary["total_expenses"]
        assert call_args["savings_rate"]   == sample_summary["savings_rate"]


class TestCompileNode:
    """Tests for FinanceAgent.compile_node()."""

    def test_compile_returns_complete_report(
        self, finance_agent, sample_summary
    ):
        """Should compile all state data into report."""
        state  = FinanceAgentState(
            transactions=[], classified=[],
            analysed    =[{"description": "Test"}],
            summary     =sample_summary,
            advice      ="Save more.",
            has_high_risk=False, error=None, report=None
        )
        result = finance_agent.compile_node(state)
        report = result["report"]
        assert "transactions"  in report
        assert "summary"       in report
        assert "advice"        in report
        assert "has_high_risk" in report
        assert "error"         in report

    def test_compile_preserves_high_risk_flag(self, finance_agent, sample_summary):
        """Should preserve has_high_risk in report."""
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=sample_summary, advice="Save more.",
            has_high_risk=True, error=None, report=None
        )
        result = finance_agent.compile_node(state)
        assert result["report"]["has_high_risk"] is True


class TestErrorNode:
    """Tests for FinanceAgent.error_node()."""

    def test_error_node_returns_report_with_error(self, finance_agent):
        """Should return report containing the error message."""
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=None, advice=None,
            has_high_risk=False,
            error="No transactions provided",
            report=None
        )
        result = finance_agent.error_node(state)
        assert result["report"]["error"] == "No transactions provided"

    def test_error_node_returns_empty_transactions(self, finance_agent):
        """Should return empty transactions list in error report."""
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=None, advice=None,
            has_high_risk=False, error="Error", report=None
        )
        result = finance_agent.error_node(state)
        assert result["report"]["transactions"] == []


# ============================================================
# Conditional Edges
# ============================================================

class TestConditionalEdges:
    """Tests for FinanceAgent conditional routing."""

    def test_route_after_validate_no_error_goes_to_classify(self, finance_agent):
        """Should route to classify_node when no error."""
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=None, advice=None,
            has_high_risk=False, error=None, report=None
        )
        assert finance_agent.route_after_validate(state) == "classify_node"

    def test_route_after_validate_with_error_goes_to_error(self, finance_agent):
        """Should route to error_node when error exists."""
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=None, advice=None,
            has_high_risk=False, error="Something went wrong", report=None
        )
        assert finance_agent.route_after_validate(state) == "error_node"

    def test_route_after_analyse_always_goes_to_summarise(self, finance_agent):
        """Should always route to summarise_node."""
        state  = FinanceAgentState(
            transactions=[], classified=[], analysed=[],
            summary=None, advice=None,
            has_high_risk=True, error=None, report=None
        )
        assert finance_agent.route_after_analyse(state) == "summarise_node"


# ============================================================
# Full Agent Run
# ============================================================

class TestFinanceAgentRun:
    """Tests for FinanceAgent.run() end-to-end."""

    def test_run_returns_report_dict(
        self, finance_agent, sample_transactions, sample_summary
    ):
        """Should return a complete report dict."""
        setup_agent_mocks(finance_agent, sample_summary)
        result = finance_agent.run({"transactions": sample_transactions})
        assert isinstance(result, dict)

    def test_run_report_contains_all_keys(
        self, finance_agent, sample_transactions, sample_summary
    ):
        """Report should contain all expected keys."""
        setup_agent_mocks(finance_agent, sample_summary)
        result = finance_agent.run({"transactions": sample_transactions})
        assert "transactions"  in result
        assert "summary"       in result
        assert "advice"        in result
        assert "has_high_risk" in result
        assert "error"         in result

    def test_run_with_empty_transactions_returns_error_report(self, finance_agent):
        """Should return error report for empty transactions."""
        result = finance_agent.run({"transactions": []})
        assert result["error"] is not None

    def test_run_with_empty_transactions_has_empty_summary(self, finance_agent):
        """Should return empty summary for error case."""
        result = finance_agent.run({"transactions": []})
        assert result["transactions"] == []

    def test_run_calls_all_chains(
        self, finance_agent, sample_transactions, sample_summary
    ):
        """Should call all chains during successful run."""
        setup_agent_mocks(finance_agent, sample_summary)
        finance_agent.run({"transactions": sample_transactions})
        assert finance_agent.classify_chain.invoke.called
        assert finance_agent.analyse_chain.invoke.called
        assert finance_agent.summarise_chain.invoke.called
        assert finance_agent.advice_chain.invoke.called

    def test_run_does_not_call_chains_for_empty_input(self, finance_agent):
        """Should not call AI chains when input is empty."""
        finance_agent.run({"transactions": []})
        finance_agent.classify_chain.invoke.assert_not_called()
        finance_agent.analyse_chain.invoke.assert_not_called()

    def test_run_graph_is_cached_after_first_call(
        self, finance_agent, sample_transactions, sample_summary
    ):
        """Graph should be built once and cached."""
        setup_agent_mocks(finance_agent, sample_summary)
        finance_agent.run({"transactions": sample_transactions})
        graph_after_first = finance_agent._graph

        setup_agent_mocks(finance_agent, sample_summary)
        finance_agent.run({"transactions": sample_transactions})
        graph_after_second = finance_agent._graph

        assert graph_after_first is graph_after_second

    def test_run_with_high_risk_transaction(
        self, finance_agent, sample_transactions, sample_summary
    ):
        """Should flag high risk in report when detected."""
        finance_agent.classify_chain.invoke.return_value  = "EXPENSE"
        finance_agent.analyse_chain.invoke.return_value   = {
            "category": "Other", "risk_level": "High"
        }
        finance_agent.summarise_chain.invoke.return_value = sample_summary
        finance_agent.advice_chain.invoke.return_value    = "Be careful."
        result = finance_agent.run({"transactions": sample_transactions})
        assert result["has_high_risk"] is True