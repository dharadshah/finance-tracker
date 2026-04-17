"""Document builder for converting Finance Tracker data to LlamaIndex documents."""
import logging
from typing import List
from llama_index.core import Document
from app.models.transaction import Transaction
from app.models.category import Category

logger = logging.getLogger("app.ai.rag.document_builder")


class TransactionDocumentBuilder:
    """Builds LlamaIndex Documents from Finance Tracker transactions.

    Each transaction becomes a Document with:
        text    : human readable description for embedding
        metadata: structured data for filtering

    Usage:
        builder   = TransactionDocumentBuilder()
        documents = builder.build_from_transactions(transactions)
    """

    def build_from_transaction(self, transaction: Transaction) -> Document:
        """Convert a single Transaction to a LlamaIndex Document.

        Args:
            transaction: SQLAlchemy Transaction model instance.

        Returns:
            LlamaIndex Document with text and metadata.
        """
        transaction_type = "EXPENSE" if transaction.is_expense else "INCOME"
        category_name    = (
            transaction.category_rel.name
            if transaction.category_rel
            else "Uncategorized"
        )

        # Text is what gets embedded and searched
        text = (
            f"{transaction.description} - "
            f"{transaction_type} - "
            f"Rs.{transaction.amount:.2f} - "
            f"Category: {category_name}"
        )

        # Metadata is used for filtering and context
        metadata = {
            "transaction_id"  : transaction.id,
            "description"     : transaction.description,
            "amount"          : transaction.amount,
            "is_expense"      : transaction.is_expense,
            "transaction_type": transaction_type,
            "category"        : category_name
        }

        logger.debug(f"Built document for transaction: {transaction.id}")
        return Document(text=text, metadata=metadata)

    def build_from_transactions(
        self,
        transactions: List[Transaction]
    ) -> List[Document]:
        """Convert a list of Transactions to LlamaIndex Documents.

        Args:
            transactions: List of SQLAlchemy Transaction model instances.

        Returns:
            List of LlamaIndex Documents.
        """
        if not transactions:
            logger.warning("No transactions provided for document building")
            return []

        documents = [
            self.build_from_transaction(t)
            for t in transactions
        ]

        logger.info(f"Built {len(documents)} documents from transactions")
        return documents

    def build_summary_document(self, summary: dict) -> Document:
        """Build a summary document from financial summary data.

        Args:
            summary: Dict with total_income, total_expenses etc.

        Returns:
            LlamaIndex Document representing the financial summary.
        """
        text = (
            f"Financial Summary: "
            f"Total Income Rs.{summary.get('total_income', 0):.2f}, "
            f"Total Expenses Rs.{summary.get('total_expenses', 0):.2f}, "
            f"Balance Rs.{summary.get('balance', 0):.2f}, "
            f"Savings Rate {summary.get('savings_rate', 0):.1f}%, "
            f"Largest Expense Category: {summary.get('largest_expense_category', 'Unknown')}"
        )

        metadata = {
            "document_type"           : "summary",
            "total_income"            : summary.get("total_income",   0),
            "total_expenses"          : summary.get("total_expenses", 0),
            "balance"                 : summary.get("balance",        0),
            "savings_rate"            : summary.get("savings_rate",   0),
            "largest_expense_category": summary.get("largest_expense_category", "Unknown")
        }

        logger.info("Built financial summary document")
        return Document(text=text, metadata=metadata)

    def build_category_document(self, category: Category) -> Document:
        """Build a document representing a category.

        Args:
            category: SQLAlchemy Category model instance.

        Returns:
            LlamaIndex Document representing the category.
        """
        transaction_count = len(category.transactions) if category.transactions else 0
        total_amount      = sum(
            t.amount for t in category.transactions
        ) if category.transactions else 0

        text = (
            f"Category: {category.name}. "
            f"{category.description or ''}. "
            f"Total transactions: {transaction_count}. "
            f"Total amount: Rs.{total_amount:.2f}."
        )

        metadata = {
            "document_type"    : "category",
            "category_id"      : category.id,
            "category_name"    : category.name,
            "transaction_count": transaction_count,
            "total_amount"     : total_amount
        }

        logger.debug(f"Built document for category: {category.name}")
        return Document(text=text, metadata=metadata)