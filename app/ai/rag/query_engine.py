"""Query engine for answering questions over indexed Finance Tracker data."""
import logging
from llama_index.core import VectorStoreIndex
from llama_index.core.query_engine import BaseQueryEngine
from app.ai.rag.index_manager import IndexManager
from app.ai.rag.document_builder import TransactionDocumentBuilder

logger = logging.getLogger("app.ai.rag.query_engine")


class FinanceQueryEngine:
    """Query engine for answering natural language questions about finances.

    Combines:
        IndexManager             -> manages the Chroma vector store
        TransactionDocumentBuilder -> converts transactions to documents
        VectorStoreIndex         -> retrieves relevant documents
        Groq LLM                 -> generates answers

    Usage:
        engine   = FinanceQueryEngine()
        engine.build_index(transactions)    # builds and persists
        response = engine.query("What did I spend most on?")

        # On next startup - load persisted index
        engine   = FinanceQueryEngine()
        engine.load_existing_index()        # loads from Chroma
        response = engine.query("...")
    """

    def __init__(self):
        self.index_manager  = IndexManager()
        self.doc_builder    = TransactionDocumentBuilder()
        self._query_engine  : BaseQueryEngine = None
        self.logger         = logging.getLogger(
            "app.ai.rag.FinanceQueryEngine"
        )

    def build_index(self, transactions: list, summary: dict = None):
        """Build and persist the vector index from transactions.

        Args:
            transactions: List of Transaction model instances.
            summary     : Optional financial summary dict to include.
        """
        self.logger.info("Building finance query index")

        documents = self.doc_builder.build_from_transactions(transactions)

        if summary:
            summary_doc = self.doc_builder.build_summary_document(summary)
            documents.append(summary_doc)

        if not documents:
            raise ValueError("No documents to index")

        index = self.index_manager.create_index(documents)
        self._build_query_engine(index)
        self.logger.info("Finance query engine ready and persisted")

    def load_existing_index(self) -> bool:
        """Load existing index from Chroma if available.

        Returns:
            True if index loaded successfully, False if no data exists.
        """
        self.logger.info("Attempting to load existing index from Chroma")
        index = self.index_manager.load_index()

        if index is None:
            self.logger.info("No existing index found in Chroma")
            return False

        self._build_query_engine(index)
        self.logger.info("Existing index loaded successfully")
        return True

    def _build_query_engine(self, index: VectorStoreIndex):
        """Build the query engine from an index.

        Args:
            index: VectorStoreIndex to build query engine from.
        """
        self._query_engine = index.as_query_engine(
            similarity_top_k = 5,
            response_mode    = "compact"
        )

    def query(self, question: str) -> dict:
        """Answer a natural language question about finances.

        Args:
            question: Natural language question about finances.

        Returns:
            Dict with answer and source documents.

        Raises:
            ValueError : If index not built yet.
            Exception  : If query fails.
        """
        if self._query_engine is None:
            raise ValueError(
                "Query engine not ready. "
                "Call build_index() or load_existing_index() first."
            )

        self.logger.info(f"Querying: {question}")
        response = self._query_engine.query(question)

        source_nodes = [
            {
                "text"  : node.text,
                "score" : round(node.score, 4) if node.score else None
            }
            for node in response.source_nodes
        ] if hasattr(response, "source_nodes") else []

        result = {
            "question": question,
            "answer"  : str(response),
            "sources" : source_nodes
        }

        self.logger.info("Query completed successfully")
        return result

    def rebuild_index(self, transactions: list, summary: dict = None):
        """Clear and rebuild the index from scratch.

        Useful when transactions are deleted or significantly changed.

        Args:
            transactions: Full list of Transaction model instances.
            summary     : Optional financial summary dict.
        """
        self.logger.info("Rebuilding index from scratch")
        self.index_manager.clear_index()
        self._query_engine = None
        self.build_index(transactions, summary)
        self.logger.info("Index rebuilt successfully")

    @property
    def is_ready(self) -> bool:
        """Check if query engine is ready."""
        return self._query_engine is not None

    @property
    def document_count(self) -> int:
        """Return number of documents in the vector store."""
        return self.index_manager.document_count