"""Prompt version evaluator for comparing prompt performance."""
import logging
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass, field
from langchain_core.output_parsers import StrOutputParser
from app.ai.llm.factory import LLMClientFactory
from app.prompts.base_prompt import BasePrompt

logger = logging.getLogger("app.ai.evaluation.prompt_evaluator")


@dataclass
class EvaluationResult:
    """Result of evaluating a single prompt on a test case.

    Attributes:
        prompt_name : Name of the prompt evaluated.
        question    : Input question or transaction.
        response    : LLM response.
        latency_ms  : Response time in milliseconds.
        passed      : Whether response met expectations.
        reason      : Why it passed or failed.
    """
    prompt_name : str
    question    : str
    response    : str
    latency_ms  : float
    passed      : bool
    reason      : str = ""


@dataclass
class EvaluationReport:
    """Complete evaluation report for a prompt.

    Attributes:
        prompt_name  : Name of the prompt evaluated.
        total        : Total number of test cases.
        passed       : Number of passing test cases.
        failed       : Number of failing test cases.
        pass_rate    : Percentage of passing test cases.
        avg_latency  : Average response latency in ms.
        results      : Individual test case results.
    """
    prompt_name : str
    total       : int
    passed      : int
    failed      : int
    pass_rate   : float
    avg_latency : float
    results     : List[EvaluationResult] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"Prompt: {self.prompt_name}\n"
            f"Pass Rate: {self.pass_rate:.1f}% "
            f"({self.passed}/{self.total})\n"
            f"Avg Latency: {self.avg_latency:.0f}ms"
        )


class PromptEvaluator:
    """Evaluates and compares prompt versions.

    Runs test cases against prompts and measures:
        Pass rate    -> percentage of expected outputs matched
        Latency      -> response time per call
        Consistency  -> same input always gives same output type

    Usage:
        evaluator = PromptEvaluator()

        test_cases = [
            {"input": {"transaction": "Salary"}, "expected": "INCOME"},
            {"input": {"transaction": "Netflix"}, "expected": "EXPENSE"}
        ]

        report = evaluator.evaluate_prompt(
            prompt     = ClassifyTransactionPrompt(),
            test_cases = test_cases,
            validator  = lambda r, e: e in r.upper()
        )
        print(report.summary())
    """

    def __init__(self):
        self.factory = LLMClientFactory()
        self.client  = self.factory.get_groq_client()
        self.logger  = logging.getLogger(
            "app.ai.evaluation.PromptEvaluator"
        )

    def evaluate_prompt(
        self,
        prompt     : BasePrompt,
        test_cases : List[Dict[str, Any]],
        validator  : callable
    ) -> EvaluationReport:
        self.logger.info(
            f"Evaluating prompt: {prompt.metadata.name} "
            f"v{prompt.metadata.version} "
            f"with {len(test_cases)} test cases"
        )

        model   = self.client.get_model()
        chain   = prompt.build() | model | StrOutputParser()
        results = []

        for case in test_cases:
            start    = time.time()
            response = chain.invoke(case["input"])
            latency  = (time.time() - start) * 1000

            passed = validator(response, case["expected"])
            result = EvaluationResult(
                prompt_name = prompt.metadata.name,
                question    = str(case["input"]),
                response    = response,
                latency_ms  = latency,
                passed      = passed,
                reason      = "matched" if passed else f"expected {case['expected']}"
            )
            results.append(result)

        passed_count = sum(1 for r in results if r.passed)
        avg_latency  = sum(r.latency_ms for r in results) / len(results)

        report = EvaluationReport(
            prompt_name = prompt.metadata.name,
            total       = len(test_cases),
            passed      = passed_count,
            failed      = len(test_cases) - passed_count,
            pass_rate   = (passed_count / len(test_cases)) * 100,
            avg_latency = avg_latency,
            results     = results
        )

        self.logger.info(f"Evaluation complete: {report.summary()}")
        return report

    def compare_prompts(
        self,
        prompts    : List[BasePrompt],
        test_cases : List[Dict[str, Any]],
        validator  : callable
    ) -> List[EvaluationReport]:
        """Compare multiple prompt versions on the same test cases.

        Args:
            prompts    : List of BasePrompt instances to compare.
            test_cases : List of test cases.
            validator  : Function(response, expected) -> bool

        Returns:
            List of EvaluationReports sorted by pass rate descending.
        """
        self.logger.info(
            f"Comparing {len(prompts)} prompt versions"
        )

        reports = [
            self.evaluate_prompt(p, test_cases, validator)
            for p in prompts
        ]

        reports.sort(key=lambda r: r.pass_rate, reverse=True)

        self.logger.info(
            f"Best prompt: {reports[0].prompt_name} "
            f"({reports[0].pass_rate:.1f}%)"
        )
        return reports