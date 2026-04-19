"""Index manager for creating and managing LlamaIndex vector stores."""
import logging
from typing import List, Optional
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from app.config.settings import settings

logger = logging.getLogger("app.ai.rag.index_manager")


class IndexManager:
    """Manages LlamaIndex vector store index lifecycle with Chroma persistence.

    Handles:
        - LLM and embedding model configuration
        - Index creation from documents
        - Index persistence via Chroma
        - Index loading from existing Chroma collection
        - Index updates when new documents arrive

    Usage:
        manager = IndexManager()
        index   = manager.create_index(documents)
        same    = manager.load_index()   # loads persisted index
    """

    def __init__(self):
        """Initialize with Groq LLM, HuggingFace embeddings and Chroma."""
        self._index          : Optional[VectorStoreIndex] = None
        self._chroma_client  = None
        self._chroma_collection = None
        self._configure_settings()
        self._configure_chroma()

    def _configure_settings(self):
        """Configure LlamaIndex global settings."""
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

    def _configure_chroma(self):
        """Configure Chroma vector store client and collection."""
        logger.info(
            f"Configuring Chroma: "
            f"persist_dir={settings.chroma_persist_dir}, "
            f"collection={settings.chroma_collection_name}"
        )

        self._chroma_client = chromadb.PersistentClient(
            path = settings.chroma_persist_dir
        )

        self._chroma_collection = self._chroma_client.get_or_create_collection(
            name = settings.chroma_collection_name
        )

        logger.info("Chroma configured successfully")

    def _get_storage_context(self) -> StorageContext:
        """Build a StorageContext backed by Chroma.

        Returns:
            StorageContext with Chroma vector store.
        """
        vector_store    = ChromaVectorStore(
            chroma_collection = self._chroma_collection
        )
        return StorageContext.from_defaults(vector_store=vector_store)

    def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create a new vector store index from documents.

        Persists to Chroma automatically.

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

        storage_context = self._get_storage_context()
        self._index     = VectorStoreIndex.from_documents(
            documents,
            storage_context = storage_context
        )

        logger.info("Index created and persisted to Chroma")
        return self._index

    def load_index(self) -> Optional[VectorStoreIndex]:
        """Load existing index from Chroma if available.

        Returns:
            VectorStoreIndex if data exists in Chroma, None otherwise.
        """
        try:
            count = self._chroma_collection.count()
            if count == 0:
                logger.info("No existing data in Chroma collection")
                return None

            logger.info(f"Loading existing index from Chroma ({count} items)")
            storage_context = self._get_storage_context()
            self._index     = VectorStoreIndex.from_vector_store(
                storage_context.vector_store
            )
            logger.info("Index loaded from Chroma successfully")
            return self._index

        except Exception as e:
            logger.warning(f"Could not load index from Chroma: {e}")
            return None

    def update_index(self, new_documents: List[Document]):
        """Add new documents to existing Chroma index.

        Args:
            new_documents: List of new Documents to add.

        Raises:
            ValueError: If index has not been created yet.
        """
        if self._index is None:
            raise ValueError(
                "Index not created yet. Call create_index() first."
            )

        logger.info(f"Adding {len(new_documents)} documents to Chroma index")
        for doc in new_documents:
            self._index.insert(doc)
        logger.info("Index updated successfully")

    def clear_index(self):
        """Clear the current index from memory and Chroma."""
        self._index = None
        try:
            self._chroma_client.delete_collection(
                settings.chroma_collection_name
            )
            self._chroma_collection = self._chroma_client.get_or_create_collection(
                name = settings.chroma_collection_name
            )
            logger.info("Chroma collection cleared and recreated")
        except Exception as e:
            logger.warning(f"Could not clear Chroma collection: {e}")

    def get_index(self) -> Optional[VectorStoreIndex]:
        """Return the current index."""
        return self._index

    @property
    def is_ready(self) -> bool:
        """Check if index is ready for querying."""
        return self._index is not None

    @property
    def document_count(self) -> int:
        """Return number of documents in Chroma collection."""
        try:
            return self._chroma_collection.count()
        except Exception:
            return 0