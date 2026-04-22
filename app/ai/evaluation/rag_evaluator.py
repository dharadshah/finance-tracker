"""RAG pipeline evaluator using TruLens."""
import logging
from typing import List, Optional
from trulens.core import TruSession, Feedback
from trulens.providers.litellm import LiteLLM
from trulens.apps.llamaindex import TruLlama
from app.config.settings import settings

logger = logging.getLogger("app.ai.evaluation.rag_evaluator")


class RAGEvaluator:
    """Evaluates RAG pipeline quality using TruLens RAG Triad.

    Measures:
        Context Relevance  -> retrieved chunks relevant to query?
        Groundedness       -> answer supported by context?
        Answer Relevance   -> answer addresses the question?

    Usage:
        evaluator = RAGEvaluator()
        evaluator.setup()
        with evaluator.instrument(query_engine) as recorder:
            response = query_engine.query("What did I spend most on?")
        evaluator.get_results()
    """

    def __init__(self):
        self.session  : Optional[TruSession]  = None
        self.provider : Optional[LiteLLM]     = None
        self.feedbacks: List[Feedback]         = []
        self.logger   = logging.getLogger(
            "app.ai.evaluation.RAGEvaluator"
        )

    def setup(self):
        """Initialize TruLens session and feedback providers.

        Uses Groq as the feedback provider for evaluation.
        """
        self.logger.info("Setting up TruLens RAG evaluator")

        self.session = TruSession()
        self.session.reset_database()

        # Use Groq as the LLM for evaluation judgments
        self.provider = LiteLLM(
            model_engine = f"groq/{settings.groq_chat_model}"
        )

        self._setup_feedbacks()
        self.logger.info("TruLens RAG evaluator ready")

    def _setup_feedbacks(self):
        """Configure the three RAG Triad feedback functions."""

        # Context Relevance
        context_relevance = (
            Feedback(
                self.provider.context_relevance,
                name = "Context Relevance"
            )
            .on_input()
            .on(TruLlama.select_source_nodes().node.text)
            .aggregate(min)
        )

        # Groundedness
        groundedness = (
            Feedback(
                self.provider.groundedness_measure_with_cot_reasons,
                name = "Groundedness"
            )
            .on(TruLlama.select_source_nodes().node.text.collect())
            .on_output()
        )

        # Answer Relevance
        answer_relevance = (
            Feedback(
                self.provider.relevance,
                name = "Answer Relevance"
            )
            .on_input()
            .on_output()
        )

        self.feedbacks = [
            context_relevance,
            groundedness,
            answer_relevance
        ]

        self.logger.info("RAG Triad feedbacks configured")

    def instrument(self, query_engine, app_id: str = "finance-tracker-rag"):
        """Wrap a query engine with TruLens instrumentation.

        Args:
            query_engine: LlamaIndex query engine to instrument.
            app_id      : Identifier for this evaluation run.

        Returns:
            TruLlama context manager for recording.
        """
        self.logger.info(f"Instrumenting query engine: {app_id}")
        return TruLlama(
            query_engine,
            app_id    = app_id,
            feedbacks = self.feedbacks
        )

    def get_results(self) -> dict:
        """Get evaluation results from the TruLens session.

        Returns:
            Dict with leaderboard metrics.
        """
        if self.session is None:
            raise ValueError("Evaluator not set up. Call setup() first.")

        leaderboard = self.session.get_leaderboard()
        self.logger.info("Evaluation results retrieved")
        return leaderboard.to_dict() if hasattr(leaderboard, "to_dict") else {}

    def run_evaluation(
        self,
        query_engine,
        test_questions: List[str],
        app_id        : str = "finance-tracker-rag"
    ) -> dict:
        """Run evaluation over a set of test questions.

        Args:
            query_engine   : LlamaIndex query engine to evaluate.
            test_questions : List of questions to test.
            app_id         : Identifier for this evaluation run.

        Returns:
            Dict with evaluation results and scores.
        """
        self.logger.info(
            f"Running evaluation with {len(test_questions)} questions"
        )

        results = []
        tru_recorder = self.instrument(query_engine, app_id)

        for question in test_questions:
            with tru_recorder as recorder:
                response = query_engine.query(question)
                results.append({
                    "question": question,
                    "answer"  : str(response)
                })

        self.logger.info("Evaluation complete")
        return {
            "results"   : results,
            "leaderboard": self.get_results()
        }