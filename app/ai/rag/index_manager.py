"""Index manager for creating and managing LlamaIndex vector stores."""
import logging
from typing import List, Optional
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.config.settings import settings

logger = logging.getLogger("app.ai.rag.index_manager")


class IndexManager:
    """Manages LlamaIndex vector store index lifecycle.

    Handles:
        - LLM and embedding model configuration
        - Index creation from documents
        - Index updates when new documents arrive
        - Index persistence (in-memory for now)

    Usage:
        manager = IndexManager()
        index   = manager.create_index(documents)
    """

    def __init__(self):
        """Initialize with Groq LLM and HuggingFace embeddings."""
        self._index     : Optional[VectorStoreIndex] = None
        self._configure_settings()

    def _configure_settings(self):
        """Configure LlamaIndex global settings.

        Uses:
            LLM       : Groq llama-3.3-70b-versatile
            Embeddings: HuggingFace BAAI/bge-small-en-v1.5 (free, local)
        """
        logger.info("Configuring LlamaIndex settings")

        Settings.llm = Groq(
            model   = "llama-3.3-70b-versatile",
            api_key = settings.groq_api_key
        )

        Settings.embed_model = HuggingFaceEmbedding(
            model_name = "BAAI/bge-small-en-v1.5"
        )

        Settings.node_parser = SentenceSplitter(
            chunk_size    = 512,
            chunk_overlap = 50
        )

        logger.info("LlamaIndex settings configured")

    def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create a new vector store index from documents.

        Args:
            documents: List of LlamaIndex Documents to index.

        Returns:
            VectorStoreIndex ready for querying.

        Raises:
            ValueError: If documents list is empty.
        """
        if not documents:
            raise ValueError("Cannot create index from empty document list")

        logger.info(f"Creating index from {len(documents)} documents")
        self._index = VectorStoreIndex.from_documents(documents)
        logger.info("Index created successfully")
        return self._index

    def update_index(self, new_documents: List[Document]):
        """Add new documents to existing index.

        Args:
            new_documents: List of new Documents to add.

        Raises:
            ValueError: If index has not been created yet.
        """
        if self._index is None:
            raise ValueError(
                "Index not created yet. Call create_index() first."
            )

        logger.info(f"Adding {len(new_documents)} documents to index")
        for doc in new_documents:
            self._index.insert(doc)
        logger.info("Index updated successfully")

    def get_index(self) -> Optional[VectorStoreIndex]:
        """Return the current index.

        Returns:
            VectorStoreIndex if created, None otherwise.
        """
        return self._index

    def clear_index(self):
        """Clear the current index from memory."""
        self._index = None
        logger.info("Index cleared")

    @property
    def is_ready(self) -> bool:
        """Check if index is ready for querying.

        Returns:
            True if index exists, False otherwise.
        """
        return self._index is not None