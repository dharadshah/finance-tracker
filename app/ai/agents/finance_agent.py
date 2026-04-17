"""Finance Tracker LangGraph agent for multi-step financial analysis."""
import logging
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from app.ai.agents.base_agent import BaseAgent
from app.ai.chains.finance_chains import (
    ClassifyTransactionChain,
    AnalyseTransactionChain,
    SummariseTransactionsChain,
    FinancialAdviceChain
)
from app.ai.llm.base_client import BaseLLMClient

logger = logging.getLogger("app.ai.agents.finance_agent")


# ============================================================
# State Definition
# ============================================================

class FinanceAgentState(TypedDict):
    """Shared state passed between all nodes in the agent.

    Attributes:
        transactions        : Raw input transactions.
        classified          : Transactions with classification added.
        analysed            : Transactions with category and risk added.
        summary             : Financial summary dict.
        advice              : Personalised financial advice string.
        has_high_risk       : True if any transaction is high risk.
        error               : Error message if something went wrong.
        report              : Final compiled report.
    """
    transactions    : List[dict]
    classified      : List[dict]
    analysed        : List[dict]
    summary         : Optional[dict]
    advice          : Optional[str]
    has_high_risk   : bool
    error           : Optional[str]
    report          : Optional[dict]


# ============================================================
# Finance Agent
# ============================================================

class FinanceAgent(BaseAgent):
    """LangGraph agent for comprehensive financial analysis.

    Workflow:
        validate -> classify -> analyse -> summarise -> advice -> compile

    Conditional routing:
        validate: no transactions  -> error_node
        validate: has transactions -> classify_node
        analyse:  high risk found  -> advice_node (with warning)
        analyse:  no high risk     -> summarise_node -> advice_node
    """

    def __init__(self, llm_client: BaseLLMClient):
        """Initialize with LLM client.

        Args:
            llm_client: BaseLLMClient providing the language model.
        """
        super().__init__()
        self.classify_chain  = ClassifyTransactionChain(llm_client)
        self.analyse_chain   = AnalyseTransactionChain(llm_client)
        self.summarise_chain = SummariseTransactionsChain(llm_client)
        self.advice_chain    = FinancialAdviceChain(llm_client)

    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    def validate_node(self, state: FinanceAgentState) -> dict:
        """Validate that transactions exist and are non-empty.

        Args:
            state: Current agent state.

        Returns:
            Updated state dict.
        """
        self.logger.info("Validating input transactions")
        transactions = state.get("transactions", [])

        if not transactions:
            self.logger.warning("No transactions provided")
            return {"error": "No transactions provided for analysis"}

        self.logger.info(f"Validated {len(transactions)} transactions")
        return {"error": None}

    def classify_node(self, state: FinanceAgentState) -> dict:
        """Classify each transaction as INCOME or EXPENSE.

        Args:
            state: Current agent state.

        Returns:
            Updated state with classified transactions.
        """
        self.logger.info("Classifying transactions")
        classified = []

        for t in state["transactions"]:
            classification = self.classify_chain.invoke({
                "transaction": t["description"]
            })
            classified.append({**t, "classification": classification})
            self.logger.debug(
                f"Classified '{t['description']}' as {classification}"
            )

        self.logger.info(f"Classified {len(classified)} transactions")
        return {"classified": classified}

    def analyse_node(self, state: FinanceAgentState) -> dict:
        """Analyse each transaction for category and risk level.

        Args:
            state: Current agent state.

        Returns:
            Updated state with analysed transactions and risk flag.
        """
        self.logger.info("Analysing transactions")
        analysed       = []
        has_high_risk  = False

        for t in state["classified"]:
            analysis = self.analyse_chain.invoke({
                "description"    : t["description"],
                "amount"         : t["amount"],
                "classification" : t["classification"]
            })
            enriched = {
                **t,
                "category"  : analysis.get("category",   "Uncategorized"),
                "risk_level": analysis.get("risk_level",  "Low")
            }
            if enriched["risk_level"] == "High":
                has_high_risk = True
                self.logger.warning(
                    f"High risk transaction: {t['description']}"
                )
            analysed.append(enriched)

        self.logger.info(
            f"Analysed {len(analysed)} transactions. "
            f"High risk: {has_high_risk}"
        )
        return {"analysed": analysed, "has_high_risk": has_high_risk}

    def summarise_node(self, state: FinanceAgentState) -> dict:
        """Generate financial summary from analysed transactions.

        Args:
            state: Current agent state.

        Returns:
            Updated state with summary dict.
        """
        self.logger.info("Generating financial summary")
        summary = self.summarise_chain.invoke({
            "transactions": state["analysed"]
        })
        self.logger.info(
            f"Summary generated: balance={summary.get('balance')}"
        )
        return {"summary": summary}

    def advice_node(self, state: FinanceAgentState) -> dict:
        """Generate personalised financial advice.

        Args:
            state: Current agent state.

        Returns:
            Updated state with advice string.
        """
        self.logger.info("Generating financial advice")
        summary = state.get("summary", {})

        advice = self.advice_chain.invoke({
            "total_income"   : summary.get("total_income",   0),
            "total_expenses" : summary.get("total_expenses", 0),
            "savings_rate"   : summary.get("savings_rate",   0),
            "top_category"   : summary.get("largest_expense_category", "Unknown")
        })

        self.logger.info("Financial advice generated")
        return {"advice": advice}

    def compile_node(self, state: FinanceAgentState) -> dict:
        """Compile final report from all state data.

        Args:
            state: Current agent state.

        Returns:
            Updated state with complete report dict.
        """
        self.logger.info("Compiling final report")
        report = {
            "transactions"  : state.get("analysed",      []),
            "summary"       : state.get("summary",        {}),
            "advice"        : state.get("advice",         ""),
            "has_high_risk" : state.get("has_high_risk", False),
            "error"         : state.get("error",          None)
        }
        self.logger.info("Report compiled successfully")
        return {"report": report}

    def error_node(self, state: FinanceAgentState) -> dict:
        """Handle error state by compiling an error report.

        Args:
            state: Current agent state.

        Returns:
            Updated state with error report.
        """
        self.logger.error(f"Agent error: {state.get('error')}")
        return {
            "report": {
                "transactions"  : [],
                "summary"       : {},
                "advice"        : "",
                "has_high_risk" : False,
                "error"         : state.get("error", "Unknown error")
            }
        }

    # --------------------------------------------------------
    # Conditional Edges
    # --------------------------------------------------------

    def route_after_validate(self, state: FinanceAgentState) -> str:
        """Route after validation.

        Returns:
            'error_node' if error exists, else 'classify_node'.
        """
        if state.get("error"):
            return "error_node"
        return "classify_node"

    def route_after_analyse(self, state: FinanceAgentState) -> str:
        """Route after analysis.

        Always routes to summarise_node — high risk is flagged
        in state but does not skip summarisation.

        Returns:
            'summarise_node' always.
        """
        return "summarise_node"

    # --------------------------------------------------------
    # Graph Builder
    # --------------------------------------------------------

    def build_graph(self):
        """Build and compile the Finance Agent StateGraph.

        Returns:
            Compiled LangGraph graph.
        """
        graph = StateGraph(FinanceAgentState)

        # Add all nodes
        graph.add_node("validate_node",  self.validate_node)
        graph.add_node("classify_node",  self.classify_node)
        graph.add_node("analyse_node",   self.analyse_node)
        graph.add_node("summarise_node", self.summarise_node)
        graph.add_node("advice_node",    self.advice_node)
        graph.add_node("compile_node",   self.compile_node)
        graph.add_node("error_node",     self.error_node)

        # Set entry point
        graph.set_entry_point("validate_node")

        # Add conditional edge after validate
        graph.add_conditional_edges(
            "validate_node",
            self.route_after_validate,
            {
                "classify_node" : "classify_node",
                "error_node"    : "error_node"
            }
        )

        # Add linear edges
        graph.add_edge("classify_node",  "analyse_node")
        graph.add_edge("analyse_node",   "summarise_node")
        graph.add_edge("summarise_node", "advice_node")
        graph.add_edge("advice_node",    "compile_node")
        graph.add_edge("compile_node",   END)
        graph.add_edge("error_node",     END)

        self.logger.info("Finance Agent graph compiled")
        return graph.compile()

    # --------------------------------------------------------
    # Run
    # --------------------------------------------------------

    def run(self, inputs: dict) -> dict:
        """Execute the Finance Agent with transaction inputs.

        Args:
            inputs: Dict containing 'transactions' list.

        Returns:
            Complete financial analysis report dict.

        Raises:
            Exception: If graph execution fails.
        """
        self.logger.info(
            f"Running Finance Agent with "
            f"{len(inputs.get('transactions', []))} transactions"
        )

        initial_state = FinanceAgentState(
            transactions  = inputs.get("transactions", []),
            classified    = [],
            analysed      = [],
            summary       = None,
            advice        = None,
            has_high_risk = False,
            error         = None,
            report        = None
        )

        graph  = self.get_graph()
        result = graph.invoke(initial_state)

        self.logger.info("Finance Agent completed successfully")
        return result.get("report", {})