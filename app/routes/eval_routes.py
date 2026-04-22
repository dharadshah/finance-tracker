"""Evaluation routes for Finance Tracker AI quality measurement."""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.routes.base_router import BaseRouter
from app.dependencies import get_db, get_settings
from app.config.settings import Settings
from app.ai.evaluation.prompt_evaluator import PromptEvaluator
from app.prompts.finance_prompts import ClassifyTransactionPrompt
from app.constants.app_constants import ROUTE_CONSTANTS

logger = logging.getLogger("app.routes.eval_routes")


class EvalRouter(BaseRouter):
    """Router handling evaluation endpoints."""

    def __init__(self):
        super().__init__(
            prefix = ROUTE_CONSTANTS.EVAL_PREFIX.value,
            tags   = ["Evaluation"]
        )

    def register(self) -> APIRouter:

        @self.router.post("/classify")
        async def evaluate_classify_prompt(
            db       : Session  = Depends(get_db),
            settings : Settings = Depends(get_settings)
        ):
            """Evaluate classification prompt quality."""
            self.logger.info("Running classify prompt evaluation")

            test_cases = [
                {"input": {"transaction": "Monthly salary credited"},   "expected": "INCOME"},
                {"input": {"transaction": "Paid electricity bill"},      "expected": "EXPENSE"},
                {"input": {"transaction": "Received freelance payment"}, "expected": "INCOME"},
                {"input": {"transaction": "Grocery shopping at D-Mart"}, "expected": "EXPENSE"},
                {"input": {"transaction": "Netflix subscription"},       "expected": "EXPENSE"},
                {"input": {"transaction": "Dividends received"},         "expected": "INCOME"},
                {"input": {"transaction": "Paid rent for apartment"},    "expected": "EXPENSE"},
                {"input": {"transaction": "Bonus from employer"},        "expected": "INCOME"}
            ]

            evaluator = PromptEvaluator()
            report    = evaluator.evaluate_prompt(
                prompt     = ClassifyTransactionPrompt(),
                test_cases = test_cases,
                validator  = lambda response, expected: expected in response.upper()
            )

            return {
                "prompt_name" : report.prompt_name,
                "total"       : report.total,
                "passed"      : report.passed,
                "failed"      : report.failed,
                "pass_rate"   : report.pass_rate,
                "avg_latency" : round(report.avg_latency, 2),
                "results"     : [
                    {
                        "question"  : r.question,
                        "response"  : r.response,
                        "expected"  : tc["expected"],
                        "passed"    : r.passed,
                        "latency_ms": round(r.latency_ms, 2)
                    }
                    for r, tc in zip(report.results, test_cases)
                ]
            }

        return self.router


router = EvalRouter().register()