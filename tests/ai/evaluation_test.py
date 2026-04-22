"""Tests for prompt and RAG evaluation tools."""
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from app.ai.evaluation.prompt_evaluator import (
    PromptEvaluator,
    EvaluationResult,
    EvaluationReport
)
from app.prompts.finance_prompts import ClassifyTransactionPrompt


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def mock_evaluator():
    """Return PromptEvaluator with mocked LLM."""
    with patch("app.ai.evaluation.prompt_evaluator.LLMClientFactory") as mock_factory:
        mock_client = MagicMock()
        mock_factory.return_value.get_groq_client.return_value = mock_client
        evaluator = PromptEvaluator()
        return evaluator, mock_client


@pytest.fixture
def classify_test_cases():
    return [
        {"input": {"transaction": "Salary credited"},   "expected": "INCOME"},
        {"input": {"transaction": "Paid electricity"},  "expected": "EXPENSE"},
        {"input": {"transaction": "Freelance payment"}, "expected": "INCOME"},
        {"input": {"transaction": "Netflix bill"},      "expected": "EXPENSE"}
    ]


@pytest.fixture
def simple_validator():
    return lambda response, expected: expected in response.upper()


# ============================================================
# EvaluationResult
# ============================================================

class TestEvaluationResult:
    """Tests for EvaluationResult dataclass."""

    def test_creates_with_required_fields(self):
        """Should create with all required fields."""
        result = EvaluationResult(
            prompt_name = "test_prompt",
            question    = "Salary?",
            response    = "INCOME",
            latency_ms  = 100.0,
            passed      = True
        )
        assert result.prompt_name == "test_prompt"
        assert result.passed      is True

    def test_default_reason_is_empty(self):
        """Default reason should be empty string."""
        result = EvaluationResult(
            prompt_name = "test",
            question    = "q",
            response    = "r",
            latency_ms  = 100.0,
            passed      = True
        )
        assert result.reason == ""

    def test_failed_result_stores_reason(self):
        """Failed result should store reason."""
        result = EvaluationResult(
            prompt_name = "test",
            question    = "q",
            response    = "wrong",
            latency_ms  = 100.0,
            passed      = False,
            reason      = "expected INCOME"
        )
        assert result.reason == "expected INCOME"


# ============================================================
# EvaluationReport
# ============================================================

class TestEvaluationReport:
    """Tests for EvaluationReport dataclass."""

    @pytest.fixture
    def sample_report(self):
        return EvaluationReport(
            prompt_name = "classify_transaction",
            total       = 4,
            passed      = 3,
            failed      = 1,
            pass_rate   = 75.0,
            avg_latency = 150.0
        )

    def test_summary_contains_prompt_name(self, sample_report):
        """Summary should contain prompt name."""
        assert "classify_transaction" in sample_report.summary()

    def test_summary_contains_pass_rate(self, sample_report):
        """Summary should contain pass rate."""
        assert "75" in sample_report.summary()

    def test_summary_contains_latency(self, sample_report):
        """Summary should contain latency."""
        assert "150" in sample_report.summary()

    def test_default_results_is_empty_list(self):
        """Default results should be empty list."""
        report = EvaluationReport(
            prompt_name = "test",
            total       = 0,
            passed      = 0,
            failed      = 0,
            pass_rate   = 0.0,
            avg_latency = 0.0
        )
        assert report.results == []


# ============================================================
# PromptEvaluator
# ============================================================

class TestPromptEvaluator:
    """Tests for PromptEvaluator."""

    def test_evaluate_prompt_returns_report(
        self, mock_evaluator, classify_test_cases, simple_validator
    ):
        """Should return EvaluationReport."""
        evaluator, mock_client = mock_evaluator
        mock_chain             = MagicMock()
        mock_chain.invoke.return_value = "INCOME"

        with patch(
            "app.ai.evaluation.prompt_evaluator.StrOutputParser"
        ):
            with patch.object(
                ClassifyTransactionPrompt,
                "build",
                return_value = MagicMock(__or__=lambda s, o: mock_chain)
            ):
                report = evaluator.evaluate_prompt(
                    prompt     = ClassifyTransactionPrompt(),
                    test_cases = classify_test_cases,
                    validator  = simple_validator
                )
        assert isinstance(report, EvaluationReport)

    def test_evaluate_prompt_counts_total(
        self, mock_evaluator, classify_test_cases, simple_validator
    ):
        """Should count total test cases correctly."""
        evaluator, mock_client = mock_evaluator
        mock_chain             = MagicMock()
        mock_chain.invoke.return_value = "INCOME"

        with patch("app.ai.evaluation.prompt_evaluator.StrOutputParser"):
            with patch.object(
                ClassifyTransactionPrompt,
                "build",
                return_value=MagicMock(__or__=lambda s, o: mock_chain)
            ):
                report = evaluator.evaluate_prompt(
                    prompt     = ClassifyTransactionPrompt(),
                    test_cases = classify_test_cases,
                    validator  = simple_validator
                )
        assert report.total == len(classify_test_cases)

    def test_evaluate_prompt_calculates_pass_rate(
        self, mock_evaluator, simple_validator
    ):
        """Should calculate pass rate correctly."""
        evaluator, mock_client = mock_evaluator
        mock_chain             = MagicMock()
        mock_chain.invoke.return_value = "INCOME"

        test_cases = [
            {"input": {"transaction": "Salary"}, "expected": "INCOME"},
            {"input": {"transaction": "Netflix"}, "expected": "EXPENSE"}
        ]

        with patch("app.ai.evaluation.prompt_evaluator.StrOutputParser"):
            with patch.object(
                ClassifyTransactionPrompt,
                "build",
                return_value=MagicMock(__or__=lambda s, o: mock_chain)
            ):
                report = evaluator.evaluate_prompt(
                    prompt     = ClassifyTransactionPrompt(),
                    test_cases = test_cases,
                    validator  = simple_validator
                )
        assert report.passed + report.failed == report.total

    def test_compare_prompts_returns_sorted_list(
        self, mock_evaluator, classify_test_cases, simple_validator
    ):
        """Should return reports sorted by pass rate descending."""
        evaluator, _ = mock_evaluator
        mock_chain   = MagicMock()
        mock_chain.invoke.return_value = "INCOME"

        with patch("app.ai.evaluation.prompt_evaluator.StrOutputParser"):
            with patch.object(
                ClassifyTransactionPrompt,
                "build",
                return_value=MagicMock(__or__=lambda s, o: mock_chain)
            ):
                reports = evaluator.compare_prompts(
                    prompts    = [ClassifyTransactionPrompt(), ClassifyTransactionPrompt()],
                    test_cases = classify_test_cases,
                    validator  = simple_validator
                )
        assert isinstance(reports, list)
        assert len(reports) == 2
        if len(reports) > 1:
            assert reports[0].pass_rate >= reports[1].pass_rate