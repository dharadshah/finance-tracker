"""Tests for LlamaIndex RAG components.

Note: Embedding model calls are mocked - no real API calls made.
"""
import pytest
import os
from unittest.mock import MagicMock, patch
from llama_index.core import Document
from app.ai.rag.document_builder import TransactionDocumentBuilder


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_transaction():
    t              = MagicMock()
    t.id           = 1
    t.description  = "Grocery Shopping"
    t.amount       = 2500.0
    t.is_expense   = True
    t.category_rel = MagicMock()
    t.category_rel.name = "Food"
    return t


@pytest.fixture
def mock_income_transaction():
    t              = MagicMock()
    t.id           = 2
    t.description  = "Salary"
    t.amount       = 50000.0
    t.is_expense   = False
    t.category_rel = MagicMock()
    t.category_rel.name = "Income"
    return t


@pytest.fixture
def mock_transaction_no_category():
    t              = MagicMock()
    t.id           = 3
    t.description  = "Cash withdrawal"
    t.amount       = 1000.0
    t.is_expense   = True
    t.category_rel = None
    return t


@pytest.fixture
def sample_summary():
    return {
        "total_income"             : 50000,
        "total_expenses"           : 2500,
        "balance"                  : 47500,
        "savings_rate"             : 95.0,
        "largest_expense_category" : "Food",
        "insight"                  : "Great savings."
    }


@pytest.fixture
def builder():
    return TransactionDocumentBuilder()


# ============================================================
# TransactionDocumentBuilder
# ============================================================

class TestTransactionDocumentBuilder:
    """Tests for TransactionDocumentBuilder."""

    def test_build_from_transaction_returns_document(
        self, builder, mock_transaction
    ):
        """Should return a LlamaIndex Document."""
        doc = builder.build_from_transaction(mock_transaction)
        assert isinstance(doc, Document)

    def test_build_from_transaction_text_contains_description(
        self, builder, mock_transaction
    ):
        """Document text should contain transaction description."""
        doc = builder.build_from_transaction(mock_transaction)
        assert "Grocery Shopping" in doc.text

    def test_build_from_transaction_text_contains_amount(
        self, builder, mock_transaction
    ):
        """Document text should contain amount."""
        doc = builder.build_from_transaction(mock_transaction)
        assert "2500" in doc.text

    def test_build_from_transaction_text_contains_type(
        self, builder, mock_transaction
    ):
        """Document text should contain transaction type."""
        doc = builder.build_from_transaction(mock_transaction)
        assert "EXPENSE" in doc.text

    def test_build_from_transaction_text_contains_category(
        self, builder, mock_transaction
    ):
        """Document text should contain category."""
        doc = builder.build_from_transaction(mock_transaction)
        assert "Food" in doc.text

    def test_build_from_income_transaction(
        self, builder, mock_income_transaction
    ):
        """Should correctly label income transactions."""
        doc = builder.build_from_transaction(mock_income_transaction)
        assert "INCOME" in doc.text

    def test_build_from_transaction_metadata_contains_id(
        self, builder, mock_transaction
    ):
        """Document metadata should contain transaction id."""
        doc = builder.build_from_transaction(mock_transaction)
        assert doc.metadata["transaction_id"] == 1

    def test_build_from_transaction_metadata_contains_amount(
        self, builder, mock_transaction
    ):
        """Document metadata should contain amount."""
        doc = builder.build_from_transaction(mock_transaction)
        assert doc.metadata["amount"] == 2500.0

    def test_build_from_transaction_metadata_contains_is_expense(
        self, builder, mock_transaction
    ):
        """Document metadata should contain is_expense."""
        doc = builder.build_from_transaction(mock_transaction)
        assert doc.metadata["is_expense"] is True

    def test_build_from_transaction_no_category_uses_uncategorized(
        self, builder, mock_transaction_no_category
    ):
        """Should use Uncategorized when category is None."""
        doc = builder.build_from_transaction(mock_transaction_no_category)
        assert "Uncategorized" in doc.text
        assert doc.metadata["category"] == "Uncategorized"

    def test_build_from_transactions_returns_list(
        self, builder, mock_transaction, mock_income_transaction
    ):
        """Should return list of Documents."""
        docs = builder.build_from_transactions(
            [mock_transaction, mock_income_transaction]
        )
        assert isinstance(docs, list)
        assert len(docs) == 2

    def test_build_from_transactions_empty_list_returns_empty(self, builder):
        """Should return empty list for empty input."""
        docs = builder.build_from_transactions([])
        assert docs == []

    def test_build_from_transactions_count_matches(
        self, builder, mock_transaction, mock_income_transaction,
        mock_transaction_no_category
    ):
        """Should return same number of documents as transactions."""
        transactions = [
            mock_transaction,
            mock_income_transaction,
            mock_transaction_no_category
        ]
        docs = builder.build_from_transactions(transactions)
        assert len(docs) == 3

    def test_build_summary_document_returns_document(
        self, builder, sample_summary
    ):
        """Should return a LlamaIndex Document for summary."""
        doc = builder.build_summary_document(sample_summary)
        assert isinstance(doc, Document)

    def test_build_summary_document_text_contains_income(
        self, builder, sample_summary
    ):
        """Summary document text should contain income."""
        doc = builder.build_summary_document(sample_summary)
        assert "50000" in doc.text

    def test_build_summary_document_text_contains_savings_rate(
        self, builder, sample_summary
    ):
        """Summary document text should contain savings rate."""
        doc = builder.build_summary_document(sample_summary)
        assert "95" in doc.text

    def test_build_summary_document_metadata_type(
        self, builder, sample_summary
    ):
        """Summary document metadata should have correct type."""
        doc = builder.build_summary_document(sample_summary)
        assert doc.metadata["document_type"] == "summary"

    def test_build_summary_document_metadata_contains_balance(
        self, builder, sample_summary
    ):
        """Summary document metadata should contain balance."""
        doc = builder.build_summary_document(sample_summary)
        assert doc.metadata["balance"] == 47500


# ============================================================
# IndexManager
# ============================================================

class TestIndexManager:
    """Tests for IndexManager."""

    @pytest.fixture(autouse=True)
    def set_testing_env(self):
        """Set IS_TESTING env var so LlamaIndex uses MockLLM."""
        os.environ["IS_TESTING"] = "1"
        yield
        os.environ.pop("IS_TESTING", None)

    def test_index_manager_initializes(self):
        """Should initialize without errors."""
        from app.ai.rag.index_manager import IndexManager
        manager = IndexManager()
        assert manager is not None

    def test_index_is_none_before_creation(self):
        """Index should be None before create_index is called."""
        from app.ai.rag.index_manager import IndexManager
        manager = IndexManager()
        assert manager.get_index() is None

    def test_is_ready_false_before_index(self):
        """is_ready should be False before index creation."""
        from app.ai.rag.index_manager import IndexManager
        manager = IndexManager()
        assert manager.is_ready is False

    def test_create_index_raises_error_for_empty_documents(self):
        """Should raise ValueError for empty document list."""
        from app.ai.rag.index_manager import IndexManager
        manager = IndexManager()
        with pytest.raises(ValueError, match="empty"):
            manager.create_index([])

    def test_clear_index_resets_to_none(self):
        """clear_index should reset index to None."""
        from app.ai.rag.index_manager import IndexManager
        manager        = IndexManager()
        manager._index = MagicMock()
        manager.clear_index()
        assert manager.get_index() is None
        assert manager.is_ready is False

# ============================================================
# FinanceQueryEngine
# ============================================================

class TestFinanceQueryEngine:
    """Tests for FinanceQueryEngine."""

    @pytest.fixture(autouse=True)
    def set_testing_env(self):
        """Set IS_TESTING env var so LlamaIndex uses MockLLM."""
        os.environ["IS_TESTING"] = "1"
        yield
        os.environ.pop("IS_TESTING", None)

    def test_query_engine_initializes(self):
        """Should initialize without errors."""
        from app.ai.rag.query_engine import FinanceQueryEngine
        engine = FinanceQueryEngine()
        assert engine is not None

    def test_is_ready_false_before_build(self):
        """is_ready should be False before build_index."""
        from app.ai.rag.query_engine import FinanceQueryEngine
        engine = FinanceQueryEngine()
        assert engine.is_ready is False

    def test_query_raises_error_when_not_ready(self):
        """Should raise ValueError when query engine not built."""
        from app.ai.rag.query_engine import FinanceQueryEngine
        engine = FinanceQueryEngine()
        with pytest.raises(ValueError, match="not ready"):
            engine.query("What did I spend most on?")

    def test_query_returns_dict(self, mock_transaction):
        """Should return dict with question, answer, sources."""
        from app.ai.rag.query_engine import FinanceQueryEngine
        engine = FinanceQueryEngine()

        mock_query_engine                    = MagicMock()
        mock_response                        = MagicMock()
        mock_response.__str__                = lambda self: "You spent most on Food."
        mock_response.source_nodes           = []
        mock_query_engine.query.return_value = mock_response
        engine._query_engine                 = mock_query_engine

        result = engine.query("What did I spend most on?")
        assert isinstance(result, dict)
        assert "question" in result
        assert "answer"   in result
        assert "sources"  in result

    def test_query_contains_original_question(self, mock_transaction):
        """Result should echo back the original question."""
        from app.ai.rag.query_engine import FinanceQueryEngine
        engine = FinanceQueryEngine()

        mock_query_engine                    = MagicMock()
        mock_response                        = MagicMock()
        mock_response.__str__                = lambda self: "Answer here."
        mock_response.source_nodes           = []
        mock_query_engine.query.return_value = mock_response
        engine._query_engine                 = mock_query_engine

        result = engine.query("What did I spend most on?")
        assert result["question"] == "What did I spend most on?"