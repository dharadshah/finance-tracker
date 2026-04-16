"""Finance Tracker prompt definitions.

All prompts are versioned classes inheriting from BasePrompt.
To add a new prompt:
    1. Create a class inheriting from BasePrompt
    2. Define metadata, system, and human properties
    3. Register it in PromptRegistry at the bottom of this file

To update a prompt:
    1. Increment the version in metadata
    2. Update system or human template
    3. Update input_vars if variables changed
"""
import logging
from app.prompts.base_prompt import BasePrompt, PromptMetadata
from app.constants.app_constants import GROQ_CHAT_MODEL

logger = logging.getLogger("app.prompts.finance_prompts")


class ClassifyTransactionPrompt(BasePrompt):
    """Classifies a transaction as INCOME or EXPENSE.

    Input variables:
        transaction: Description of the transaction to classify.

    Output:
        Single word - either INCOME or EXPENSE.
    """

    @property
    def metadata(self) -> PromptMetadata:
        return PromptMetadata(
            name        = "classify_transaction",
            version     = "1.0.0",
            description = "Classifies a transaction as INCOME or EXPENSE",
            input_vars  = ["transaction"]
        )

    @property
    def system(self) -> str:
        return (
            "You are a financial assistant for a Personal Finance Tracker. "
            "Reply with only one word: INCOME or EXPENSE. "
            "Never include any other text in your response."
        )

    @property
    def human(self) -> str:
        return """
Examples:
Transaction: "Monthly salary credited"     -> INCOME
Transaction: "Paid electricity bill"       -> EXPENSE
Transaction: "Received freelance payment"  -> INCOME
Transaction: "Grocery shopping at D-Mart"  -> EXPENSE

Now classify:
Transaction: "{transaction}" ->
"""


class AnalyseTransactionPrompt(BasePrompt):
    """Analyses a single transaction for category and risk level.

    Input variables:
        description     : Transaction description.
        amount          : Transaction amount.
        classification  : INCOME or EXPENSE.

    Output:
        JSON with keys: category, risk_level
    """

    @property
    def metadata(self) -> PromptMetadata:
        return PromptMetadata(
            name        = "analyse_transaction",
            version     = "1.0.0",
            description = "Analyses a transaction for category and risk level",
            input_vars  = ["description", "amount", "classification"]
        )

    @property
    def system(self) -> str:
        return (
            "You are a financial analyst for a Personal Finance Tracker. "
            "Always return valid JSON with no extra text, no markdown, "
            "no code blocks."
        )

    @property
    def human(self) -> str:
        return """
Analyse this transaction:
Description : {description}
Amount      : Rs.{amount}
Type        : {classification}

Return JSON with exactly these keys:
  category   : string (e.g. Food, Housing, Entertainment, Income, Utilities)
  risk_level : string (one of: Low, Medium, High)
"""


class SummariseTransactionsPrompt(BasePrompt):
    """Generates a financial summary from a list of transactions.

    Input variables:
        transactions: List of transaction dicts.

    Output:
        JSON with keys: total_income, total_expenses, balance,
                        savings_rate, largest_expense_category, insight
    """

    @property
    def metadata(self) -> PromptMetadata:
        return PromptMetadata(
            name        = "summarise_transactions",
            version     = "1.0.0",
            description = "Generates AI financial summary from transactions",
            input_vars  = ["transactions"]
        )

    @property
    def system(self) -> str:
        return """
You are a financial analyst assistant for a Personal Finance Tracker API.
Analyse transaction data and provide clear, actionable financial insights.
Always base your analysis on the actual transaction data provided.
Never make assumptions about transactions not in the data.
Always return valid JSON in this exact format with no extra text,
no markdown, no code blocks:
{{
    "total_income"              : 0,
    "total_expenses"            : 0,
    "balance"                   : 0,
    "savings_rate"              : 0,
    "largest_expense_category"  : "",
    "insight"                   : ""
}}
Keep the insight concise - maximum 2 sentences.
"""

    @property
    def human(self) -> str:
        return "Analyse these transactions and return the JSON summary: {transactions}"


class FinancialAdvicePrompt(BasePrompt):
    """Generates personalised financial advice based on summary data.

    Input variables:
        total_income    : Total income amount.
        total_expenses  : Total expenses amount.
        savings_rate    : Savings rate percentage.
        top_category    : Largest expense category.

    Output:
        Plain text financial advice, 3-5 sentences.
    """

    @property
    def metadata(self) -> PromptMetadata:
        return PromptMetadata(
            name        = "financial_advice",
            version     = "1.0.0",
            description = "Generates personalised financial advice",
            input_vars  = [
                "total_income",
                "total_expenses",
                "savings_rate",
                "top_category"
            ]
        )

    @property
    def system(self) -> str:
        return (
            "You are a personal financial advisor. "
            "Give practical, actionable advice based on the user's actual numbers. "
            "Be specific, not generic. "
            "Keep your response to 3-5 sentences."
        )

    @property
    def human(self) -> str:
        return """
My financial summary this month:
Total Income    : Rs.{total_income}
Total Expenses  : Rs.{total_expenses}
Savings Rate    : {savings_rate}%
Biggest Expense : {top_category}

What specific advice do you have for me?
"""


# ============================================================
# Prompt Registry
# ============================================================

class PromptRegistry:
    """Central registry of all available prompts.

    Usage:
        registry = PromptRegistry()
        prompt   = registry.get("classify_transaction")
        template = prompt.build()

    To add a new prompt:
        Register it in _prompts dict below.
    """

    def __init__(self):
        self._prompts: dict[str, BasePrompt] = {
            "classify_transaction"  : ClassifyTransactionPrompt(),
            "analyse_transaction"   : AnalyseTransactionPrompt(),
            "summarise_transactions": SummariseTransactionsPrompt(),
            "financial_advice"      : FinancialAdvicePrompt()
        }

    def get(self, name: str) -> BasePrompt:
        """Get a prompt by name.

        Args:
            name: Prompt name as registered in the registry.

        Returns:
            BasePrompt instance.

        Raises:
            KeyError: If prompt name is not found.
        """
        if name not in self._prompts:
            raise KeyError(
                f"Prompt '{name}' not found. "
                f"Available prompts: {self.list()}"
            )
        logger.debug(f"Retrieved prompt: {name}")
        return self._prompts[name]

    def list(self) -> list[str]:
        """List all registered prompt names.

        Returns:
            List of prompt name strings.
        """
        return list(self._prompts.keys())

    def register(self, prompt: BasePrompt):
        """Register a new prompt at runtime.

        Args:
            prompt: BasePrompt instance to register.
        """
        name = prompt.metadata.name
        self._prompts[name] = prompt
        logger.info(f"Registered prompt: {name} v{prompt.metadata.version}")


# module level registry instance
prompt_registry = PromptRegistry()