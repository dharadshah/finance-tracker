"""Comprehensive tests for Finance Tracker prompt classes.

Coverage:
    BasePrompt          -> validation, build, format, repr
    ClassifyTransactionPrompt
    AnalyseTransactionPrompt
    SummariseTransactionsPrompt
    FinancialAdvicePrompt
    PromptRegistry
"""
import pytest
from langchain_core.prompts import ChatPromptTemplate
from app.prompts.base_prompt import BasePrompt, PromptMetadata
from app.prompts.finance_prompts import (
    ClassifyTransactionPrompt,
    AnalyseTransactionPrompt,
    SummariseTransactionsPrompt,
    FinancialAdvicePrompt,
    PromptRegistry,
    prompt_registry
)


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def classify_prompt():
    return ClassifyTransactionPrompt()


@pytest.fixture
def analyse_prompt():
    return AnalyseTransactionPrompt()


@pytest.fixture
def summarise_prompt():
    return SummariseTransactionsPrompt()


@pytest.fixture
def advice_prompt():
    return FinancialAdvicePrompt()


@pytest.fixture
def registry():
    return PromptRegistry()


@pytest.fixture
def sample_transactions():
    return [
        {"description": "Salary",   "amount": 50000, "is_expense": False, "category": "Income"},
        {"description": "Grocery",  "amount": 2500,  "is_expense": True,  "category": "Food"},
        {"description": "Netflix",  "amount": 649,   "is_expense": True,  "category": "Entertainment"},
    ]


# ============================================================
# BasePrompt — via concrete subclass
# ============================================================

class TestBasePromptValidation:
    """Tests for BasePrompt._validate() via concrete subclass."""

    def test_valid_prompt_builds_successfully(self, classify_prompt):
        """Should build without errors for valid prompt."""
        template = classify_prompt.build()
        assert template is not None

    def test_build_returns_chat_prompt_template(self, classify_prompt):
        """Should return a LangChain ChatPromptTemplate."""
        template = classify_prompt.build()
        assert isinstance(template, ChatPromptTemplate)

    def test_prompt_with_empty_name_raises_error(self):
        """Should raise ValueError when metadata name is empty."""
        class InvalidPrompt(BasePrompt):
            @property
            def metadata(self):
                return PromptMetadata(name="", version="1.0.0", description="test")
            @property
            def system(self):
                return "system"
            @property
            def human(self):
                return "human"

        with pytest.raises(ValueError, match="name"):
            InvalidPrompt().build()

    def test_prompt_with_empty_version_raises_error(self):
        """Should raise ValueError when metadata version is empty."""
        class InvalidPrompt(BasePrompt):
            @property
            def metadata(self):
                return PromptMetadata(name="test", version="", description="test")
            @property
            def system(self):
                return "system"
            @property
            def human(self):
                return "human"

        with pytest.raises(ValueError, match="version"):
            InvalidPrompt().build()

    def test_prompt_with_empty_system_raises_error(self):
        """Should raise ValueError when system message is empty."""
        class InvalidPrompt(BasePrompt):
            @property
            def metadata(self):
                return PromptMetadata(name="test", version="1.0.0", description="test")
            @property
            def system(self):
                return ""
            @property
            def human(self):
                return "human"

        with pytest.raises(ValueError, match="system"):
            InvalidPrompt().build()

    def test_prompt_with_empty_human_raises_error(self):
        """Should raise ValueError when human message is empty."""
        class InvalidPrompt(BasePrompt):
            @property
            def metadata(self):
                return PromptMetadata(name="test", version="1.0.0", description="test")
            @property
            def system(self):
                return "system"
            @property
            def human(self):
                return ""

        with pytest.raises(ValueError, match="human"):
            InvalidPrompt().build()


class TestBasePromptFormat:
    """Tests for BasePrompt.format()."""

    def test_format_returns_two_messages(self, classify_prompt):
        """Should return exactly two messages - system and human."""
        messages = classify_prompt.format(transaction="Salary credited")
        assert len(messages) == 2

    def test_format_first_message_is_system(self, classify_prompt):
        """First message should be system type."""
        messages = classify_prompt.format(transaction="Salary credited")
        assert messages[0].type == "system"

    def test_format_second_message_is_human(self, classify_prompt):
        """Second message should be human type."""
        messages = classify_prompt.format(transaction="Salary credited")
        assert messages[1].type == "human"

    def test_format_injects_variable_into_human_message(self, classify_prompt):
        """Variable value should appear in human message."""
        messages = classify_prompt.format(transaction="Netflix subscription")
        assert "Netflix subscription" in messages[1].content

    def test_format_missing_required_variable_raises_error(self, classify_prompt):
        """Should raise ValueError when required variable is missing."""
        with pytest.raises(ValueError, match="missing required variables"):
            classify_prompt.format()

    def test_format_extra_variables_are_ignored(self, classify_prompt):
        """Extra variables beyond required ones should not cause errors."""
        messages = classify_prompt.format(
            transaction = "Salary",
            extra_var   = "ignored"
        )
        assert len(messages) == 2


class TestBasePromptRepr:
    """Tests for BasePrompt.__repr__()."""

    def test_repr_contains_class_name(self, classify_prompt):
        """Repr should contain class name."""
        assert "ClassifyTransactionPrompt" in repr(classify_prompt)

    def test_repr_contains_prompt_name(self, classify_prompt):
        """Repr should contain prompt name."""
        assert "classify_transaction" in repr(classify_prompt)

    def test_repr_contains_version(self, classify_prompt):
        """Repr should contain version."""
        assert "1.0.0" in repr(classify_prompt)


# ============================================================
# PromptMetadata
# ============================================================

class TestPromptMetadata:
    """Tests for PromptMetadata dataclass."""

    def test_metadata_default_author(self):
        """Should use default author when not provided."""
        metadata = PromptMetadata(name="test", version="1.0.0", description="test")
        assert metadata.author == "Finance Tracker"

    def test_metadata_default_input_vars(self):
        """Should use empty list for input_vars when not provided."""
        metadata = PromptMetadata(name="test", version="1.0.0", description="test")
        assert metadata.input_vars == []

    def test_metadata_custom_values(self):
        """Should store all custom values correctly."""
        metadata = PromptMetadata(
            name        = "custom",
            version     = "2.0.0",
            description = "Custom prompt",
            author      = "Dhara",
            input_vars  = ["var1", "var2"]
        )
        assert metadata.name        == "custom"
        assert metadata.version     == "2.0.0"
        assert metadata.description == "Custom prompt"
        assert metadata.author      == "Dhara"
        assert metadata.input_vars  == ["var1", "var2"]


# ============================================================
# ClassifyTransactionPrompt
# ============================================================

class TestClassifyTransactionPrompt:
    """Tests for ClassifyTransactionPrompt."""

    def test_metadata_name(self, classify_prompt):
        """Should have correct prompt name."""
        assert classify_prompt.metadata.name == "classify_transaction"

    def test_metadata_version(self, classify_prompt):
        """Should have correct version."""
        assert classify_prompt.metadata.version == "1.0.0"

    def test_metadata_input_vars(self, classify_prompt):
        """Should require transaction variable."""
        assert "transaction" in classify_prompt.metadata.input_vars

    def test_system_message_not_empty(self, classify_prompt):
        """System message should not be empty."""
        assert len(classify_prompt.system.strip()) > 0

    def test_human_message_contains_transaction_placeholder(self, classify_prompt):
        """Human message should contain {transaction} placeholder."""
        assert "{transaction}" in classify_prompt.human

    def test_human_message_contains_examples(self, classify_prompt):
        """Human message should contain few-shot examples."""
        assert "INCOME"  in classify_prompt.human
        assert "EXPENSE" in classify_prompt.human

    def test_format_income_transaction(self, classify_prompt):
        """Should format income transaction correctly."""
        messages = classify_prompt.format(transaction="Salary credited")
        assert "Salary credited" in messages[1].content

    def test_format_expense_transaction(self, classify_prompt):
        """Should format expense transaction correctly."""
        messages = classify_prompt.format(transaction="Paid rent")
        assert "Paid rent" in messages[1].content

    def test_format_empty_transaction_string(self, classify_prompt):
        """Should still format with empty transaction string."""
        messages = classify_prompt.format(transaction="")
        assert len(messages) == 2

    def test_format_missing_transaction_raises_error(self, classify_prompt):
        """Should raise ValueError when transaction is missing."""
        with pytest.raises(ValueError, match="transaction"):
            classify_prompt.format()

    def test_system_instructs_single_word_response(self, classify_prompt):
        """System message should instruct single word response."""
        assert "one word" in classify_prompt.system.lower() or \
               "single"   in classify_prompt.system.lower() or \
               "only"     in classify_prompt.system.lower()


# ============================================================
# AnalyseTransactionPrompt
# ============================================================

class TestAnalyseTransactionPrompt:
    """Tests for AnalyseTransactionPrompt."""

    def test_metadata_name(self, analyse_prompt):
        """Should have correct prompt name."""
        assert analyse_prompt.metadata.name == "analyse_transaction"

    def test_metadata_version(self, analyse_prompt):
        """Should have correct version."""
        assert analyse_prompt.metadata.version == "1.0.0"

    def test_metadata_input_vars_complete(self, analyse_prompt):
        """Should require all three input variables."""
        assert "description"    in analyse_prompt.metadata.input_vars
        assert "amount"         in analyse_prompt.metadata.input_vars
        assert "classification" in analyse_prompt.metadata.input_vars

    def test_human_contains_all_placeholders(self, analyse_prompt):
        """Human message should contain all required placeholders."""
        assert "{description}"    in analyse_prompt.human
        assert "{amount}"         in analyse_prompt.human
        assert "{classification}" in analyse_prompt.human

    def test_system_instructs_json_output(self, analyse_prompt):
        """System message should instruct JSON output."""
        assert "json" in analyse_prompt.system.lower()

    def test_human_mentions_expected_output_keys(self, analyse_prompt):
        """Human message should mention expected output keys."""
        assert "category"   in analyse_prompt.human.lower()
        assert "risk_level" in analyse_prompt.human.lower()

    def test_format_with_all_variables(self, analyse_prompt):
        """Should format correctly with all required variables."""
        messages = analyse_prompt.format(
            description    = "Netflix subscription",
            amount         = 649,
            classification = "EXPENSE"
        )
        assert "Netflix subscription" in messages[1].content
        assert "649"                  in messages[1].content
        assert "EXPENSE"              in messages[1].content

    def test_format_missing_description_raises_error(self, analyse_prompt):
        """Should raise ValueError when description is missing."""
        with pytest.raises(ValueError):
            analyse_prompt.format(amount=649, classification="EXPENSE")

    def test_format_missing_amount_raises_error(self, analyse_prompt):
        """Should raise ValueError when amount is missing."""
        with pytest.raises(ValueError):
            analyse_prompt.format(description="Netflix", classification="EXPENSE")

    def test_format_missing_classification_raises_error(self, analyse_prompt):
        """Should raise ValueError when classification is missing."""
        with pytest.raises(ValueError):
            analyse_prompt.format(description="Netflix", amount=649)

    def test_format_missing_all_variables_raises_error(self, analyse_prompt):
        """Should raise ValueError when all variables are missing."""
        with pytest.raises(ValueError):
            analyse_prompt.format()

    def test_format_with_income_transaction(self, analyse_prompt):
        """Should format correctly for income transactions."""
        messages = analyse_prompt.format(
            description    = "Freelance payment",
            amount         = 15000,
            classification = "INCOME"
        )
        assert "INCOME" in messages[1].content


# ============================================================
# SummariseTransactionsPrompt
# ============================================================

class TestSummariseTransactionsPrompt:
    """Tests for SummariseTransactionsPrompt."""

    def test_metadata_name(self, summarise_prompt):
        """Should have correct prompt name."""
        assert summarise_prompt.metadata.name == "summarise_transactions"

    def test_metadata_version(self, summarise_prompt):
        """Should have correct version."""
        assert summarise_prompt.metadata.version == "1.0.0"

    def test_metadata_input_vars(self, summarise_prompt):
        """Should require transactions variable."""
        assert "transactions" in summarise_prompt.metadata.input_vars

    def test_system_instructs_json_output(self, summarise_prompt):
        """System message should instruct JSON output."""
        assert "json" in summarise_prompt.system.lower()

    def test_system_contains_all_output_keys(self, summarise_prompt):
        """System message should define all expected output keys."""
        assert "total_income"             in summarise_prompt.system
        assert "total_expenses"           in summarise_prompt.system
        assert "balance"                  in summarise_prompt.system
        assert "savings_rate"             in summarise_prompt.system
        assert "largest_expense_category" in summarise_prompt.system
        assert "insight"                  in summarise_prompt.system

    def test_format_with_transaction_list(self, summarise_prompt, sample_transactions):
        """Should format correctly with list of transactions."""
        messages = summarise_prompt.format(transactions=sample_transactions)
        assert len(messages) == 2
        assert "Salary" in messages[1].content

    def test_format_with_empty_transaction_list(self, summarise_prompt):
        """Should format correctly with empty list."""
        messages = summarise_prompt.format(transactions=[])
        assert len(messages) == 2

    def test_format_missing_transactions_raises_error(self, summarise_prompt):
        """Should raise ValueError when transactions is missing."""
        with pytest.raises(ValueError):
            summarise_prompt.format()

    def test_system_instructs_no_markdown(self, summarise_prompt):
        """System message should instruct no markdown output."""
        assert "markdown" in summarise_prompt.system.lower() or \
               "no extra"  in summarise_prompt.system.lower()


# ============================================================
# FinancialAdvicePrompt
# ============================================================

class TestFinancialAdvicePrompt:
    """Tests for FinancialAdvicePrompt."""

    def test_metadata_name(self, advice_prompt):
        """Should have correct prompt name."""
        assert advice_prompt.metadata.name == "financial_advice"

    def test_metadata_version(self, advice_prompt):
        """Should have correct version."""
        assert advice_prompt.metadata.version == "1.0.0"

    def test_metadata_input_vars_complete(self, advice_prompt):
        """Should require all four input variables."""
        assert "total_income"   in advice_prompt.metadata.input_vars
        assert "total_expenses" in advice_prompt.metadata.input_vars
        assert "savings_rate"   in advice_prompt.metadata.input_vars
        assert "top_category"   in advice_prompt.metadata.input_vars

    def test_human_contains_all_placeholders(self, advice_prompt):
        """Human message should contain all required placeholders."""
        assert "{total_income}"   in advice_prompt.human
        assert "{total_expenses}" in advice_prompt.human
        assert "{savings_rate}"   in advice_prompt.human
        assert "{top_category}"   in advice_prompt.human

    def test_format_with_all_variables(self, advice_prompt):
        """Should format correctly with all required variables."""
        messages = advice_prompt.format(
            total_income   = 50000,
            total_expenses = 10000,
            savings_rate   = 80,
            top_category   = "Housing"
        )
        assert "50000"   in messages[1].content
        assert "10000"   in messages[1].content
        assert "80"      in messages[1].content
        assert "Housing" in messages[1].content

    def test_format_missing_total_income_raises_error(self, advice_prompt):
        """Should raise ValueError when total_income is missing."""
        with pytest.raises(ValueError):
            advice_prompt.format(
                total_expenses = 10000,
                savings_rate   = 80,
                top_category   = "Housing"
            )

    def test_format_missing_savings_rate_raises_error(self, advice_prompt):
        """Should raise ValueError when savings_rate is missing."""
        with pytest.raises(ValueError):
            advice_prompt.format(
                total_income   = 50000,
                total_expenses = 10000,
                top_category   = "Housing"
            )

    def test_format_missing_all_variables_raises_error(self, advice_prompt):
        """Should raise ValueError when all variables are missing."""
        with pytest.raises(ValueError):
            advice_prompt.format()

    def test_format_zero_income(self, advice_prompt):
        """Should format correctly with zero income."""
        messages = advice_prompt.format(
            total_income   = 0,
            total_expenses = 0,
            savings_rate   = 0,
            top_category   = "None"
        )
        assert len(messages) == 2

    def test_format_high_savings_rate(self, advice_prompt):
        """Should format correctly with high savings rate."""
        messages = advice_prompt.format(
            total_income   = 100000,
            total_expenses = 10000,
            savings_rate   = 90,
            top_category   = "Food"
        )
        assert "90" in messages[1].content


# ============================================================
# PromptRegistry
# ============================================================

class TestPromptRegistry:
    """Tests for PromptRegistry."""

    def test_get_classify_transaction_prompt(self, registry):
        """Should return ClassifyTransactionPrompt by name."""
        prompt = registry.get("classify_transaction")
        assert isinstance(prompt, ClassifyTransactionPrompt)

    def test_get_analyse_transaction_prompt(self, registry):
        """Should return AnalyseTransactionPrompt by name."""
        prompt = registry.get("analyse_transaction")
        assert isinstance(prompt, AnalyseTransactionPrompt)

    def test_get_summarise_transactions_prompt(self, registry):
        """Should return SummariseTransactionsPrompt by name."""
        prompt = registry.get("summarise_transactions")
        assert isinstance(prompt, SummariseTransactionsPrompt)

    def test_get_financial_advice_prompt(self, registry):
        """Should return FinancialAdvicePrompt by name."""
        prompt = registry.get("financial_advice")
        assert isinstance(prompt, FinancialAdvicePrompt)

    def test_get_nonexistent_prompt_raises_key_error(self, registry):
        """Should raise KeyError for unknown prompt name."""
        with pytest.raises(KeyError):
            registry.get("nonexistent_prompt")

    def test_get_empty_name_raises_key_error(self, registry):
        """Should raise KeyError for empty prompt name."""
        with pytest.raises(KeyError):
            registry.get("")

    def test_list_returns_all_four_prompts(self, registry):
        """Should list all four registered prompts."""
        names = registry.list()
        assert len(names)                      == 4
        assert "classify_transaction"          in names
        assert "analyse_transaction"           in names
        assert "summarise_transactions"        in names
        assert "financial_advice"              in names

    def test_list_returns_list_type(self, registry):
        """Should return a list type."""
        assert isinstance(registry.list(), list)

    def test_register_new_prompt(self, registry):
        """Should successfully register a new prompt."""
        class NewPrompt(BasePrompt):
            @property
            def metadata(self):
                return PromptMetadata(
                    name       = "new_prompt",
                    version    = "1.0.0",
                    description= "New test prompt",
                    input_vars = ["input"]
                )
            @property
            def system(self):
                return "System message"
            @property
            def human(self):
                return "Human message {input}"

        registry.register(NewPrompt())
        assert "new_prompt" in registry.list()

    def test_register_overwrites_existing_prompt(self, registry):
        """Should overwrite existing prompt with same name."""
        original_count = len(registry.list())
        registry.register(ClassifyTransactionPrompt())
        assert len(registry.list()) == original_count

    def test_module_level_registry_is_prompt_registry_instance(self):
        """Module level prompt_registry should be PromptRegistry instance."""
        assert isinstance(prompt_registry, PromptRegistry)

    def test_module_level_registry_has_all_prompts(self):
        """Module level prompt_registry should have all prompts registered."""
        names = prompt_registry.list()
        assert "classify_transaction"   in names
        assert "analyse_transaction"    in names
        assert "summarise_transactions" in names
        assert "financial_advice"       in names

    def test_retrieved_prompt_is_buildable(self, registry):
        """Every registered prompt should be buildable."""
        for name in registry.list():
            prompt   = registry.get(name)
            template = prompt.build()
            assert isinstance(template, ChatPromptTemplate)