"""Abstract base class for all LangGraph agents."""
import logging
from abc import ABC, abstractmethod
from typing import Any
from langgraph.graph import StateGraph


class BaseAgent(ABC):
    """Abstract base class for all Finance Tracker agents.

    All agents must implement:
        build_graph() -> constructs the StateGraph
        run()         -> executes the graph with inputs

    Usage:
        agent  = FinanceAgent(llm_client)
        result = agent.run({"transactions": [...]})
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"app.ai.agents.{self.__class__.__name__}"
        )
        self._graph = None

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build and return the compiled StateGraph.

        Returns:
            Compiled LangGraph StateGraph.
        """
        pass

    @abstractmethod
    def run(self, inputs: dict) -> Any:
        """Execute the agent with inputs.

        Args:
            inputs: Dict of input values for the agent.

        Returns:
            Agent output.
        """
        pass

    def get_graph(self):
        """Get or build the compiled graph.

        Lazily compiles on first call and caches.

        Returns:
            Compiled graph instance.
        """
        if self._graph is None:
            self.logger.info(
                f"Building graph for {self.__class__.__name__}"
            )
            self._graph = self.build_graph()
        return self._graph

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"