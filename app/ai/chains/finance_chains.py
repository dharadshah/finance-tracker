"""Finance Tracker LangChain chain implementations."""
import json
import logging
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers.json import JsonOutputParser
from app.ai.chains.base_chain import BaseChain
from app.ai.llm.base_client import BaseLLMClient
from app.prompts.base_prompt import BasePrompt
from app.prompts.finance_prompts import (
    ClassifyTransactionPrompt,
    AnalyseTransactionPrompt,
    SummariseTransactionsPrompt,
    FinancialAdvicePrompt
)

logger = logging.getLogger("app.ai.chains.finance_chains")


class ClassifyTransactionChain(BaseChain):
    """Chain for classifying a transaction as INCOME or EXPENSE.

    Input  : {"transaction": "description string"}
    Output : "INCOME" or "EXPENSE" (sanitized string)
    """

    def __init__(self, llm_client: BaseLLMClient):
        super().__init__(llm_client)
        self._prompt = ClassifyTransactionPrompt()

    @property
    def prompt(self) -> BasePrompt:
        return self._prompt

    def build(self) -> Runnable:
        """Build classify chain with sanitization."""
        template = self._prompt.build()
        model    = self.llm_client.get_model()
        parser   = StrOutputParser()
        return template | model | parser

    def invoke(self, inputs: dict) -> str:
        """Invoke and sanitize output to INCOME or EXPENSE.

        Args:
            inputs: {"transaction": "description"}

        Returns:
            "INCOME" or "EXPENSE"
        """
        raw    = super().invoke(inputs)
        result = "INCOME" if "INCOME" in raw.upper() else "EXPENSE"
        self.logger.info(f"Classification result: {result}")
        return result


class AnalyseTransactionChain(BaseChain):
    """Chain for analysing a transaction for category and risk level.

    Input  : {"description": str, "amount": float, "classification": str}
    Output : {"category": str, "risk_level": str}
    """

    def __init__(self, llm_client: BaseLLMClient):
        super().__init__(llm_client)
        self._prompt = AnalyseTransactionPrompt()

    @property
    def prompt(self) -> BasePrompt:
        return self._prompt

    def build(self) -> Runnable:
        template = self._prompt.build()
        model    = self.llm_client.get_model()
        parser   = StrOutputParser()
        return template | model | parser

    def invoke(self, inputs: dict) -> dict:
        """Invoke and parse JSON response.

        Args:
            inputs: {"description": str, "amount": float, "classification": str}

        Returns:
            {"category": str, "risk_level": str}
        """
        raw     = super().invoke(inputs)
        cleaned = raw.strip().replace("```json", "").replace("```", "")
        result  = json.loads(cleaned)
        self.logger.info(f"Analysis result: {result}")
        return result


class SummariseTransactionsChain(BaseChain):
    """Chain for generating a financial summary from transactions.

    Input  : {"transactions": list}
    Output : {
        "total_income"             : float,
        "total_expenses"           : float,
        "balance"                  : float,
        "savings_rate"             : float,
        "largest_expense_category" : str,
        "insight"                  : str
    }
    """

    def __init__(self, llm_client: BaseLLMClient):
        super().__init__(llm_client)
        self._prompt = SummariseTransactionsPrompt()

    @property
    def prompt(self) -> BasePrompt:
        return self._prompt

    def build(self) -> Runnable:
        template = self._prompt.build()
        model    = self.llm_client.get_model()
        parser   = StrOutputParser()
        return template | model | parser

    def invoke(self, inputs: dict) -> dict:
        """Invoke and parse JSON summary response.

        Args:
            inputs: {"transactions": list of transaction dicts}

        Returns:
            Financial summary dict.
        """
        raw     = super().invoke(inputs)
        cleaned = raw.strip().replace("```json", "").replace("```", "")
        result  = json.loads(cleaned)
        self.logger.info(
            f"Summary generated: balance={result.get('balance')}"
        )
        return result


class FinancialAdviceChain(BaseChain):
    """Chain for generating personalised financial advice.

    Input  : {
        "total_income"   : float,
        "total_expenses" : float,
        "savings_rate"   : float,
        "top_category"   : str
    }
    Output : str (plain text advice)
    """

    def __init__(self, llm_client: BaseLLMClient):
        super().__init__(llm_client)
        self._prompt = FinancialAdvicePrompt()

    @property
    def prompt(self) -> BasePrompt:
        return self._prompt

    def build(self) -> Runnable:
        template = self._prompt.build()
        model    = self.llm_client.get_model()
        parser   = StrOutputParser()
        return template | model | parser

    def invoke(self, inputs: dict) -> str:
        """Invoke and return plain text advice.

        Args:
            inputs: Financial summary variables.

        Returns:
            Plain text financial advice string.
        """
        result = super().invoke(inputs)
        self.logger.info("Financial advice generated")
        return result.strip()