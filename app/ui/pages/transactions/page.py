"""Transactions page UI for Finance Tracker."""
import gradio as gr
import logging
from app.ui.pages import BasePage
from app.ui.state.session import SessionState

logger = logging.getLogger("app.models.transaction")


class TransactionsPage(BasePage):
    """Transactions management page."""

    def __init__(self, session: SessionState):
        self.session = session

    @property
    def title(self) -> str:
        return "Transactions"

    def build(self) -> gr.Blocks:
        with gr.Blocks(title="Finance Tracker - Transactions") as transactions_ui:
            gr.Markdown("# Transactions")
            gr.Markdown("Manage your income and expenses here.")

            # placeholder - will be built out in next step
            gr.Markdown("Coming soon - full transactions UI")

        return transactions_ui